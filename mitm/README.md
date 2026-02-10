## MITM Starter Template

This directory is a starter template for the MITM portion of the assignment.

### What you need to implement
- Capture traffic between the web app and database.
- Analyze packets for sensitive data and explain the impact.
- Record your findings.
- Include evidence (pcap files or screenshots) alongside your report.

### Getting started
1. Run your capture workflow from this directory or the repo root.
2. Save artifacts (pcap or screenshots) in this folder.
3. Document everything.

#### Command 1
`sudo docker network ls`

| NETWORK ID        | NAME                                | DRIVER | SCOPE |
|------------------|-------------------------------------|--------|-------|
| 2e47ba4cb6a3     | bridge                              | bridge | local |
| 71a002255822     | csce413_assignment2_vulnerable_network | bridge | local |
| af921099d39c     | host                                | host   | local |
| 83a1225a22fe     | none                                | null   | local |


#### Command 2
`sudo tcpdump -i br-71a002255822 -A -s 0 'port 3306'`

#### Captured Flag
`FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}`
