kubectl delete deploy connfun-kube-auth
docker rmi connfun.com/auth:latest
docker build -t connfun.com/auth:latest .
kubectl apply -f deployment.yaml
docker rm $(docker ps -aqf "status=exited")
