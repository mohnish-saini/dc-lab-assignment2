Chat Room (3-node) - Simple Python Implementation
===============================================

Files:
  - server.py   : run on Server VM (Chat-server)
  - client.py   : run on Client VMs (Client-1 & Client-2)
  - dme_ra.py   : distributed mutual exclusion middleware used by clients

Ports (recommended):
  - Server: 5000
  - Client-1 DME: 6002
  - Client-2 DME: 6003

Azure Network Security Group:
  Allow TCP 22 (SSH) from your IP.
  Allow TCP 5000, 6002, 6003 within VNet/subnet (private IP range).

Run instructions:

1) Server VM (Chat-server)
    python3 server.py

2) Client-1 VM (Client-1)
    python3 client.py --id client1 --listen-port 6002 --server-ip <SERVER_PRIVATE_IP> --peer-id client2 --peer-ip <CLIENT2_PRIVATE_IP> --peer-port 6003

3) Client-2 VM (Client-2)
    python3 client.py --id client2 --listen-port 6003 --server-ip <SERVER_PRIVATE_IP> --peer-id client1 --peer-ip <CLIENT1_PRIVATE_IP> --peer-port 6002

In the client app, use:
  chat> view
  chat> post hello team
  chat> exit
