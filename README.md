# Auto Builder Microservice

![Code Coverage](./coverage.svg)

## useful cmds
kubectl rollout restart deployment nginx-rewrite

kubectl get pods
kubectl exec -it <pod-name> -- sh


kubectl port-forward svc/test-service 8080:80


kubectl logs -l app=nginx-rewrite --tail=50
