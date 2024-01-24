FROM alpine:3.12

RUN apk add ca-certificates

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /etc/apk/repositories \
    # 安装python3
    && apk add --update --no-cache python3 py3-pip \
    && rm -rf /var/cache/apk/*

COPY . /app

WORKDIR /app

RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
    && pip config set global.trusted-host mirrors.cloud.tencent.com \
    && pip install --upgrade pip \
    # pip install scipy 等数学包失败，可使用 apk add py3-scipy 进行， 参考安装 https://pkgs.alpinelinux.org/packages?name=py3-scipy&branch=v3.13
    && pip install --user -r requirements.txt

EXPOSE 80

CMD ["python3", "app.py", "0.0.0.0", "80"]