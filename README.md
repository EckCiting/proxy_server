The Server and Client should be deployed on 2 different machines

### Install requirements

```bash
pip install -r requirements.txt
```

### Start Server

```bash
python3 server.py [SERVER IP] [SERVER PORT] [CIPHER]
```

Example:

```bash
python3 server.py 192.168.0.132 8388 ChaCha20
```

### Start Client

```bash
python3 local.py [LOCAL IP] [LOCAL PORT] [SERVER IP] [SERVER PORT] [CIPHER]
```

Example:

```bash
python3 local.py 192.168.0.137 1080 192.168.0.132 8388 ChaCha20
```

### Use Proxy

connect to socks5://[local ip]:[local port]

Example:

socks5://192.168.0.137:1080