# w251_hw12 by abhisha@berkeley.edu

This homework is based off: https://github.com/MIDS-scaling-up/v2/tree/master/week12/hw

The current setup for the Vms in the /etc/hosts file looks like this
```
127.0.0.1               localhost.localdomain localhost
10.28.81.14             gpfs1
10.28.81.16             gpfs2
10.28.81.17             gpfs3 
```

We were able to successfully provision the GPFS servers on the 3 VMs
```
[root@gpfs1 ~]# mmgetstate -a

 Node number  Node name        GPFS state
-------------------------------------------
       1      gpfs1            active
       2      gpfs2            active
       3      gpfs3            active

```
