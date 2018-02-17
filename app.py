from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask import Flask, request
from flask_mysqldb import MySQL
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, start_http_server, Summary, Counter, Histogram
import psutil
import resource,time,json



app = FlaskAPI(__name__)
prome = 'http://pushgateway.deploybytes.com'

print(prome)



# Promethesus
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


def getMetrics():
    # Server side metrics monitoring
    # CPU Percentage
    cpu_percentage = int(psutil.cpu_percent())
    cpu_percent.set(cpu_percentage)
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
    app.after_request(after_request)

# MySQL connection
app.config['MYSQL_HOST'] = 'qpairboto.cnryqwkkelel.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Qpair@2013'
app.config['MYSQL_DB'] = 'QPAIR'
mysql = MySQL(app)



notes = {
   0: 'Test Flask app0',
    1: 'Test Flask app1',
    2: 'Test Flask app2',
}

def note_repr(key):
    return {
        'url': request.host_url.rstrip('/') + url_for('notes_detail', key=key),
        'text': notes[key]
    }


@app.route("/", methods=['GET', 'POST'])
def notes_list():
    
    
    """
    List or create notes.
    """
    if request.method == 'POST':
        note = str(request.data.get('text', ''))
        idx = max(notes.keys()) + 1
        notes[idx] = note
        mysql_connection = mysql.connection.cursor()
        mysql_connection.execute('''SELECT testRunId FROM testresultparent ORDER BY updatedAt DESC LIMIT 1;''')
        testrunid_data = mysql_connection.fetchall()
        rm_tuple = testrunid_data[0]
        rm = rm_tuple[0]
        testrunid = str(rm)
        getMetrics()
        push_to_gateway(prome, job=testrunid, registry=registry)
        return "successful"

    elif request.method == 'GET':
        mysql_connection = mysql.connection.cursor()
        mysql_connection.execute('''SELECT testRunId FROM testresultparent ORDER BY updatedAt DESC LIMIT 1;''')
        testrunid_data = mysql_connection.fetchall()
        rm_tuple = testrunid_data[0]
        rm = rm_tuple[0]
        testrunid = str(rm)
        getMetrics()
        push_to_gateway(prome, job=testrunid, registry=registry)
        return [note_repr(idx) for idx in sorted(notes.keys())]


@app.route("/<int:key>", methods=['PUT', 'DELETE'])
def notes_detail(key):
    

    """
    Retrieve, update or delete note instances.
    """
    if request.method == 'PUT':
        note = str(request.data.get('text', ''))
        notes[key] = note
        mysql_connection = mysql.connection.cursor()
        mysql_connection.execute('''SELECT testRunId FROM testresultparent ORDER BY updatedAt DESC LIMIT 1;''')
        testrunid_data = mysql_connection.fetchall()
        rm_tuple = testrunid_data[0]
        rm = rm_tuple[0]
        testrunid = str(rm)
        getMetrics()
        push_to_gateway(prome, job=testrunid, registry=registry)
        return note_repr(key)

    elif request.method == 'DELETE':
        notes.pop(key, None)
        mysql_connection = mysql.connection.cursor()
        mysql_connection.execute('''SELECT testRunId FROM testresultparent ORDER BY updatedAt DESC LIMIT 1;''')
        testrunid_data = mysql_connection.fetchall()
        rm_tuple = testrunid_data[0]
        rm = rm_tuple[0]
        testrunid = str(rm)
        getMetrics()
        push_to_gateway(prome, job=testrunid, registry=registry)
        return 'Deleted successfully'

    
if __name__ == "__main__":
    start_http_server(8000)
    app.before_request(before_request)
    app.run(host='0.0.0.0', port=5000)
