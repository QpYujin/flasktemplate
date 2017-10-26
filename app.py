from flask import Flask, request
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, start_http_server, Summary, Counter, Histogram
import psutil
import resource,time,json


app = Flask(__name__)
registry = CollectorRegistry()


FLASK_REQUEST_LATENCY = Histogram('flask_request_latency_seconds', 'Flask Request Latency',['method', 'endpoint'], registry=registry)
#FLASK_REQUEST_COUNT = Counter('flask_request_count', 'Flask Request Count',['method', 'endpoint', 'http_status'], registry=registry)

def before_request():
    request.start_time = time.time()


def after_request(response):
    request_latency = time.time() - request.start_time
    FLASK_REQUEST_LATENCY.labels(request.method, request.path).observe(request_latency)


    return response


memory_usage = Gauge('mem_usage','memory_usage',registry=registry)
cpu_percent = Gauge('cpu_percent','CPU_PERCENT',registry=registry)
bytes_sent = Gauge('bytes_sent','BYTES_SENT',registry=registry)
bytes_recv = Gauge('bytes_recv','BYTES_RECV',registry=registry)
disk_usage = Gauge('disk_usage','DISK_USAGE',registry=registry)
disk_free = Gauge('disk_free','DISK_FREE',registry=registry)
status = Gauge('status','STATUS',registry=registry)
packets_sent = Gauge('packets_sent','PACKETS_SENT',registry=registry)
packets_recv = Gauge('packets_recv','PACKETS_RECV',registry=registry)
disk_readcount = Gauge('disk_readcount','DISK_READCOUNT', registry=registry)
disk_writecount = Gauge('disk_writecount','DISK_WRITECOUNT', registry=registry)
disk_readbytes = Gauge('disk_readbytes','DISK_READBYTES', registry=registry)
disk_writebytes = Gauge('disk_writebyte','DISK_WRITEBYTES', registry=registry)



@app.route('/<string:jobname>/<string:pushgateway>')
def getDetails(jobname,pushgateway):
    testrunid = str(jobname)
    pushgateway_id = str(pushgateway)

    # Server side metrics monitoring
    # CPU Percentage
    cpu_percentage = int(psutil.cpu_percent())
    cpu_percent.set(cpu_percentage)
    print cpu_percentage

    # Memory Usage
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memory_usage.set(mem_usage)

    # Network IN and OUT
    network_data = psutil.net_io_counters(pernic=True)
    network_list = list(network_data.values())
    bytes_data = list(network_list)[1]
    byte_sent = list(bytes_data)[0]
    byte_recv = list(bytes_data)[1]
    packet_sent = list(bytes_data)[2]
    packet_recv = list(bytes_data)[3]

    bytes_sent.set(byte_sent)
    bytes_recv.set(byte_recv)
    packets_sent.set(packet_sent)
    packets_recv.set(packet_recv)


    # disk status in bytes
    disk = psutil.disk_usage('/')
    disk_used = list(disk)[1]
    disk_avail = list(disk)[2]
    disk_usage.set(disk_used)
    disk_free.set(disk_avail)

    # disk counter
    disk_count = psutil.disk_io_counters(perdisk=False)
    read_count = list(disk_count)[0]
    disk_readcount.set(read_count)
    write_count = list(disk_count)[1]
    disk_writecount.set(write_count)
    read_bytes = list(disk_count)[2]
    disk_readbytes.set(read_bytes)
    write_bytes = list(disk_count)[3]
    disk_writebytes.set(write_bytes)

    #Application
    print pushgateway_id
    app.after_request(after_request)

    push_to_gateway(pushgateway_id, job=testrunid, registry=registry)

    return "result"

if __name__ == '__main__':
    start_http_server(8000)
    app.before_request(before_request)
    app.run(host='0.0.0.0', port=5000 )
  
