from service.tcp_client import TCPClient
import time

client = TCPClient(
    host="localhost",
    port=12345,
    sampling_rate=1000.0,
    n_channels=32,
    samples_per_packet=18,
    buffer_seconds=10.0,
)

try:
    print("Connecting to localhost:12345...")
    client.connect()
    print("Connected!")

    for i in range(100):
        client.receive_data()
        if client.has_data():
            data = client.get_data()
            print(f"Iter {i}: shape={data.shape}, samples={data.shape[1]}")
        time.sleep(0.1)

finally:
    print("Disconnecting...")
    client.disconnect()
    print("Done.")