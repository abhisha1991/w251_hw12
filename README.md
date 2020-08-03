# w251_hw12 by abhisha@berkeley.edu

## Part 1

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

[root@gpfs1 ~]# mmlscluster

GPFS cluster information
========================
  GPFS cluster name:         gpfs1.gpfs1
  GPFS cluster id:           17502596657464854352
  GPFS UID domain:           gpfs1.gpfs1
  Remote shell command:      /usr/bin/ssh
  Remote file copy command:  /usr/bin/scp
  Repository type:           CCR

 Node  Daemon node name  IP address   Admin node name  Designation
-------------------------------------------------------------------
   1   gpfs1             10.28.81.14  gpfs1            quorum-manager-perfmon
   2   gpfs2             10.28.81.16  gpfs2            quorum-perfmon
   3   gpfs3             10.28.81.17  gpfs3            quorum-manager-perfmon
```

Disk structure on the main node

```
[root@gpfs1 ~]# fdisk -l

Disk /dev/xvdb: 2147 MB, 2147483648 bytes, 4194304 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x00025cdb

    Device Boot      Start         End      Blocks   Id  System
/dev/xvdb1              63     4192964     2096451   82  Linux swap / Solaris

Disk /dev/xvda: 26.8 GB, 26843545600 bytes, 52428800 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x000440dc

    Device Boot      Start         End      Blocks   Id  System
/dev/xvda1   *        2048     2099199     1048576   83  Linux
/dev/xvda2         2099200    52428799    25164800   83  Linux

Disk /dev/xvdc: 26.8 GB, 26843545600 bytes, 52428800 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/xvdh: 67 MB, 67125248 bytes, 131104 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x00000000

    Device Boot      Start         End      Blocks   Id  System

Disk /dev/xvde: 107.4 GB, 107374182400 bytes, 209715200 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes

```

The below snippet shows that the nsd disks are configured on gpfs1

```
[root@gpfs1 ~]# mmlsnsd -m

 Disk name       NSD volume ID      Device          Node name or Class       Remarks
-------------------------------------------------------------------------------------------
 gpfs1nsd        0A1C510E5F21CEF3   /dev/xvde       gpfs1                    server node
 gpfs2nsd        0A1C51105F21CEF3   /dev/xvde       gpfs2                    server node
 gpfs3nsd        0A1C51115F21CEF4   /dev/xvde       gpfs3                    server node
```

Finally, we see we were able to configure the 300 GB distributed disk space utilizing all 3 nodes' individual disks

```
[root@gpfs1 gpfsfpo]# df -h .
Filesystem      Size  Used Avail Use% Mounted on
gpfsfpo         300G  2.6G  298G   1% /gpfs/gpfsfpo
```

## Part 2

For downloading AUS Gutenberg - About 4k books, 1GB of text, it took around 2 hours to download all the books

```
[root@gpfs1 gpfsfpo]# du -sh aus_gutemberg_dataset/
1.1G    aus_gutemberg_dataset/
```

For downloading the reddit data, we partitioned the 163 URL files into 3 folders (url1, url2, url3). Each of these folders will be processed by their corresponding GPFS Vm, ie, gpfs1 will process all the urls stored under "url1" and so on. Further, within each main url folder (such as url1), we partitioned 3 sub folders within it (named 1, 2 and 3). The idea for further partitioning is to be able to parallelize the processing within a single Vm. Each Vm can run multiple threads (in this case, we run 3 threads that process the urls under sub folders 1, 2 and 3 respectively). We used a custom crawler script (see this repository) to run these parallel threads to process contents under the sub folders (1, 2, 3) for a given main folder like url1.

In total we had 9 threads that were running (3 per machine). We started the python crawler in the background on each main machine like this:
```
[root@gpfs2 url2]# nohup python3 custom_crawler.py &
[1] 25257
[root@gpfs2 url2]# nohup: ignoring input and appending output to ‘nohup.out’

[root@gpfs2 url2]# ls
1  2  3  custom_crawler.py  nohup.out

[root@gpfs2 url2]# jobs
[1]+  Running                 nohup python3 custom_crawler.py &
[root@gpfs2 url2]#
```
It is important to run the processes in the background so that they continue running even if the ssh connection disconnects.

At the time of this writing, there were around 25 MB worth of data that was written to the output "reddit" folder
```
[root@gpfs1 ~]# du -sh /gpfs/gpfsfpo/reddit
25M     /gpfs/gpfsfpo/reddit
[root@gpfs1 ~]#
```

We can monitor the number of files in the output "reddit" folder like this:
```
[root@gpfs1 reddit]#  ls -1 | wc -l
3429
[root@gpfs1 reddit]#  ls -1 | wc -l
3441
[root@gpfs1 reddit]#  ls -1 | wc -l
3458
[root@gpfs1 reddit]#  ls -1 | wc -l
3466
```
The number of files visible to the 3 machines should be the same because they share the same output destination folder
