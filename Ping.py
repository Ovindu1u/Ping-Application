from socket import *
import struct
import time
import random
import sys

def calc_checksum(icmp_type, icmp_code, id, seq, data):

    packet = struct.pack("BBHHH", icmp_type, icmp_code, 0, id, seq) + data
    if len(packet) % 2 != 0:
        packet += b'\x00'

    packet = [(packet[i] << 8) + packet[i+1] for i in range(0, len(packet), 2)]
    sum = 0

    for value in packet:
        sum += value

    while (sum >> 16) > 0:
        sum = (sum & 0xFFFF) + (sum >> 16)
    
    checksum = ~sum & 0xFFFF #NOT to get 1s complement & with FFFF to get 16bits
    

    checksum, = struct.unpack(">H", struct.pack("H", checksum))

    return checksum

def send_ping(s, destination, seq, size):

    data = random.randbytes(size)
    checksum = calc_checksum(8, 0, 1, seq, data)
    packet = struct.pack("BBHHH", 8, 0, checksum, 1, seq) + data
    send_time = time.time()
    s.sendto(packet, (destination, 0) )
    return send_time

def receive_ping(s, size, seq):

    try:
        response, sender = s.recvfrom(size + 1024)
        recv_time = time.time()
        data = response[28:len(response)]
        type, code, checksum, id, res_seq = struct.unpack("BBHHH", response[20:28])
        ttl = response[8]
        calculated_checksum = calc_checksum(type, code, id, seq, data)

        if((checksum == calculated_checksum) & (id == 1) & (res_seq == seq) & (type == 0) & (code == 0)):
            status = "SUCCESS"
        elif((type == 11) & (code == 0)):
            status = "EXPIRED"

        return status, sender[0], recv_time, ttl, len(data), res_seq
    except TimeoutError:
        return "TIMEOUT", '', 0, 0, 0, 0

def print_statistics(sent, received, time_list):

    max_time = total_time = 0
    for time in time_list:
        total_time += time
        if time > max_time:
            max_time = time

    min_time = max_time
    for time in time_list:
        if time < min_time:
            min_time = time

    success = round(received / sent * 100)

    print(f"\nSent = {sent}, Received = {received}, Lost = {sent - received} ({success}% success)")
    if total_time > 0:
        avg_time = round(total_time / received)
        print(f"\nMinimum = {min_time}ms, Maximum = {max_time}ms, Average = {avg_time}ms")

def ping(destination, timeout, ttl, count, size):

    s = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
    s.setsockopt(SOL_IP, IP_TTL, ttl)
    s.settimeout(timeout)
    sent = received = seq = 0
    time_list = []

    print(f"Pinging {destination} with {size} bytes:")
    while count > 0:

        time.sleep(1)
        send_time = send_ping(s, destination, seq, size)
        sent += 1
        status, sender, recv_time, res_ttl, data_len, res_seq = receive_ping(s, size, seq)

        match(status):
            case("SUCCESS"):
                received += 1
                rtt = round((recv_time - send_time) * 1000)
                time_list.append(rtt)
                print(f"Reply from {sender}: seq={res_seq} bytes={data_len} time={rtt}ms TTL={res_ttl}")

            case ("EXPIRED"):
                print(f"Reply from {sender}: TTL expired!")

            case ("TIMEOUT"):
                print("Request timed out!")

        seq += 1
        count -= 1
    
    print_statistics(sent, received, time_list)
    


def print_help():
    print("Usage: ping <destination> <options...>\n") 
    print("Options:")
    print(" -t timeout      Time in seconds to wait for each reply")
    print(" -l live         Time to Live")
    print(" -c count        Number of Echo Ping requests")
    print(" -s size         ICMP ping payload size")

def proccess_args(args):
    timeout = 2
    ttl = 128 #live
    count = 4
    size = 64

    for i, arg in enumerate(args):

        try:
            match(arg):
                case '-t' | '--timeout':
                    timeout = int(args[i+1])
                case '-l' | '--live':
                    ttl = int(args[i+1])
                case '-c' | '--count':
                    count = int(args[i+1])
                case '-s' | '--size':
                    size = int(args[i+1])
                case _:
                    if arg[0] == '-':
                        raise SyntaxError
                     
        except ValueError:
            print(f"{args[i+1]} is a bad value for option for {arg}")
        except SyntaxError:
            print(f"Unknown option {arg}\n")
            print_help()

    return timeout, ttl, count, size

def main():
    args = sys.argv
    if len(args) > 1:
        hostname = args[1]
        args = args[2:len(args)]
        timeout, ttl, count, size = proccess_args(args)
        ping(hostname, timeout, ttl, count, size)
    else:
        print_help()

  
main()










    