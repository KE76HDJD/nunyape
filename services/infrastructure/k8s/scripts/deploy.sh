#!/bin/bash
kubectl apply -f k8s/
kubectl rollout restart deployment/auth-service