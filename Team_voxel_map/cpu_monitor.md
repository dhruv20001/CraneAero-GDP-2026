Run:

	top

This opens a real-time system monitor.

Key CPU line:

%Cpu(s):  5.3 us,  1.2 sy,  0.0 ni, 92.8 id,  0.4 wa

Meaning:

	us – user processes

	sy – system (kernel)

	ni – nice processes

	id – idle CPU

	wa – I/O wait

👉 CPU usage ≈ 100 − idle

Example:

	100 - 92.8 = 7.2% CPU usage

Exit with q

Get the infos
use the PID number obatined in top
then:
	pidstat -p <PID> 1

Exemple :

	12:10:01   PID  %usr %system  %CPU
	12:10:02 12345  25.00  10.00  35.00

PID  %MEM   RSS   CMD
12345  3.2  450000 octomap_server
