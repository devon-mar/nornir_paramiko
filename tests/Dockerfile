FROM alpine:latest
RUN apk add --no-cache dropbear dropbear-scp
RUN mkdir /root/.ssh/ \
    && echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEq2cLqs++uwJh6xLTy4nX20UDfbgb6cDZl2nNkJEKud" > /root/.ssh/authorized_keys
ENTRYPOINT ["dropbear", "-EFR"]
