Chat Room (3-node) - Simple Python Implementation
===============================================

Files:
  - server.py   : run on Server VM (Node-1)
  - client.py   : run on Client VMs (Node-2 & Node-3)
  - dme_ra.py   : distributed mutual exclusion middleware (Ricart–Agrawala) used by clients

Ports (recommended):
  - Server: 5000
  - Client-1 DME: 6002
  - Client-2 DME: 6003

Azure NSG:
  Allow TCP 22 (SSH) from your IP.
  Allow TCP 5000, 6002, 6003 within VNet/subnet (private IP range).

Run instructions:

1) Server VM (Node-1)
    python3 server.py

2) Client-1 VM (Node-2)
    python3 client.py --id client1 --listen-port 6002 --server-ip <SERVER_PRIVATE_IP> --peer-id client2 --peer-ip <CLIENT2_PRIVATE_IP> --peer-port 6003

3) Client-2 VM (Node-3)
    python3 client.py --id client2 --listen-port 6003 --server-ip <SERVER_PRIVATE_IP> --peer-id client1 --peer-ip <CLIENT1_PRIVATE_IP> --peer-port 6002

In the client app, use:
  chat> view
  chat> post hello team
  chat> exit
