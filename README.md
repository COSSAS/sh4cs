<div align="center">
<a href="https://gitlab.com/cossas/sh4cs/-/tree/master"><img src="img/SH4CS-logo.jpg" height="100px" />

![Website](https://img.shields.io/badge/website-cossas--project.org-orange)
</div></a>

<hr style="border:2px solid gray"> </hr>
<div align="center">
SH4CS extends Kubernetes with regeneration and self-healing properties inspired by the human immune system.</div>
<hr style="border:2px solid gray"> </hr>

_All COSSAS projects are hosted on [GitLab](https://gitlab.com/cossas/sh4cs/) with a push mirror to GitHub. For issues/contributions check [CONTRIBUTING.md](https://gitlab.com/cossas/home/-/blob/main/CONTRIBUTING.md)_ 


# Self-Healing for Cyber Security 2.0 (SH4CS)


RELEASED: March 6th, 2025\
LANGUAGE: Python\
LICENSE: Apache 2.0


## Documentation
Documentation of the source code can be found through [docs].

## Context and background
In the continuous battle between cyber attackers and defenders, the ultimate objective is to make software and systems autonomously cyber resilient. One way to implement autonomous resilience on the software deployment level is provided by TNO’s Self-Healing for Cyber Security (SH4CS) software, inspired by biological defence mechanisms.

It makes use of defensive mechanisms of the human body, where from three fundamental properties of the immune system inspiration is taken from, to make their systems autonomously resilient:

1.	**Disposability**: cell duplication and programmed or targeted cell death results in continuous cell regeneration, eliminating undetected abnormalities and reducing the likelihood of successful infections. Disposability of body cells is a prerequisite for the effectiveness of the immune system.
2.	**Distribution**: the more local the defence mechanism, the faster (but also less targeted) the response. The innate immune system acts much faster than the adaptive immune system, which in turn is faster than immunization.
3.	**Response proportionality**: the innate immune system is always the first line of defence. The more energy-consuming adaptive immune system is only activated to support the innate one when and where necessary.

The current SH4CS software primarily consists of Python code that implements (a) a decentralized rule system – also referred to as ‘Lymphocyte software’ – that executes healing functionality for an individual application container (by running as a sidecar in the same Kubernetes POD), (b) a metrics processor that enables the specification of monitorable metrics (using the Prometheus open source software) that will alert the Lymphocyte software. The software code was developed for deployment in modern container platforms empowered by Kubernetes and Prometheus.

An architecture diagram can be found [here](img/architecture_overview_SH4CS_realized.png), alongside a more elaborate diagram of what the vision of Self-Healing for Cyber Security looks like. The draw.io files are included.


## Running the demos locally

### Preparing minikube
First make sure that you have [minikube](https://minikube.sigs.k8s.io/docs/start/) installed, then start a local minikube cluster.
```shell
minikube start
```

Next build the development images
```shell
docker compose -f compose.build.yaml build
```

Then load the development images into the cluster so we don't have to deal with pulling images from a (private) repository
```shell
minikube image load ci.tno.nl:4567/tri/self-healing/sh4cs2-testbed/lymphocyte:development
minikube image load ci.tno.nl:4567/tri/self-healing/sh4cs2-testbed/testapp:development
minikube image load ci.tno.nl:4567/tri/self-healing/sh4cs2-testbed/scenario-tester:development
```

Next, apply all manifests at once
```shell
kubectl apply -k manifests/
```


### Regeneration demo

The regeneration demo demonstrates the pod becoming unready 450 seconds after the lympho has started, and restarting the test application 600s after the lympho has started (there can be some discrepancy ).

This demo is already running after applying the manifests.

Simply watch the regeneration deployment
```shell
kubectl get pod --watch -l app=regeneration-demo
```
Or the events related to the pod
```shell
kubectl events --for "pod/$(kubectl get pods -l app=regeneration-demo --output jsonpath='{.items[0].metadata.name}')" --watch
```

Or using the included monitor
```shell
kubectl exec deploy/scenario-tester -it -- /opt/app/monitor.py
```

Then look at the `regeneration-demo` deployment.
Its readiness probe should turn red after 75% of the TTL has passed, and should restart after 100% of the TTL has passed.

![](examples/regeneration-demo.mp4)


### Threat-level demo

This demo demonstrates increments in threat levels.
In this scenario there are two ways to fire prometheus alerts:
- Perform failed logins
- Generate download file errors (status code 404)
Each of these alerts lets the threat-level increment by one.
When the the threat-level is 2, and either of the alerts fire, then the application will be restarted.

To get this demo running, start the included monitor:
```shell
kubectl exec deploy/scenario-tester -it -- /opt/app/monitor.py
```

Next, in a different shell execute the script
```shell
kubectl exec deploy/scenario-tester -it -- /opt/app/test-scenario-bruteforce.py
```

![](examples/bruteforce-demo.mp4)

### Passing threat-level demo

This demo demonstrates threat levels being passed to other applications.
When the threat-level of `testapp` is zero, the `testapp2` is not rate-limited, but in response to the threat-level of `testapp` becoming nonzero, the `testapp2` becomes rate-limited.
Like in previous demos, a way to trigger an increase of the threat-level of `testapp` is to perform failed logins.

To get this demo running, start the included monitor:
```shell
kubectl exec deploy/scenario-tester -it -- /opt/app/monitor.py
```

Next, in a different shell execute the script
```shell
kubectl exec deploy/scenario-tester -it -- /opt/app/test-scenario-rate-limiter.py
```

![](examples/rate-limiter-demo.mp4)


### Proxying readiness/liveness probes

This demo demonstrated the ability to perform readiness and liveness probes from the lympho container to the application container.
The application container's readiness and liveness probe endpoints can be set at will using an api.
Meanwhile, the liveness probe of the application container points to the lympho container, which gives the latter the ability to restart the application container via probes.

To get this demo running, start the included monitor:
```shell
kubectl exec deploy/scenario-tester -it -- /opt/app/monitor.py
```

Next, in a different shell execute the script
```shell
kubectl exec deploy/scenario-tester -it -- /opt/app/test-scenario-healthcheck.py
```

![](examples/healthcheck-demo.mp4)

## Source project
V.1.0 of this software was originally developed within the Partnership for Cyber Security Innovation (PCSI), a Dutch innovation ecosystem that features leading companies across several industries. V2.0 builds on feedback from PCSI partners and additional insights, and was fully developed by TNO.
