


```sh
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 \
-nodes -keyout RootCA.key -out RootCA.crt -subj "/CN=Example-Root-CA" \
-addext "subjectAltName=DNS:example.com,DNS:*.example.com,IP:10.0.0.1"
```

## Links

* https://learn.microsoft.com/en-us/azure/application-gateway/self-signed-certificates
