Output regeneration-demo.mp4

Set FontSize 12
Set Width 1500
Set Height 750
Set Padding 50

Hide
Type "cd .. && clear" Enter
Show

Sleep 1

Type "kubectl apply -k manifests/" Enter

Wait
Sleep 1

Hide
  Type@10ms "tmux -f /dev/null -L test new-session -- bash --norc" Enter
  # Vertically split tmux
  Type@10ms "tmux split-window -d -v -- bash --norc && \" Enter
  Type@10ms "tmux set status && \" Enter
  Type@10ms 'tmux setw pane-border-style "fg=0" && \' Enter
  Type@10ms 'tmux setw pane-active-border-style "fg=0"' Enter
  Sleep 0.5
  Ctrl+L
  Sleep 1

  Ctrl+B
  Type ":resize-pane -U 15" Enter
Show

Type "watch --no-title -n1 kubectl get pod -l app=regeneration-demo"
Sleep 1
Enter

Ctrl+B
Type o

Sleep 5

Type `kubectl exec deploy/scenario-tester -it -- /opt/app/monitor.py`
Sleep 1
Enter

# Wait for containers to start
Sleep 15


Hide
Sleep 410
Show
Sleep 40
Hide
Sleep 110
Show
Sleep 40




Hide
Ctrl+C
Sleep 0.5

Ctrl+B
Type ":kill-session" Enter
Sleep 1

Type "clear" Enter

Type "kubectl delete -k manifests/" Enter
Wait

Sleep 5
