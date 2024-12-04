# Dedicated for debugging JS part

'''
data example
1) RC input
'RC inputs values - 0:{}; '
'1:{}; 2:{}; 3:{}; '
'4:{}; 5:{}; 6:{}; '
'7:{}; 8:{}; 9:{};'.format(
                    self.rc_v[0],
                    self.rc_v[1], self.rc_v[2], self.rc_v[3],
                    self.rc_v[4], self.rc_v[5], self.rc_v[6],
                    self.rc_v[7], self.rc_v[8], self.rc_v[9])

'RC inputs values. 0: "{}"'
                '1: "{}" 2: "{}" 3: "{}" '
                '4: "{}" 5: "{}" 6: "{}" '
                '7: "{}" 8: "{}" 9: "{}"'
                .format(
                    self.rc_v[0],
                    self.rc_v[1], self.rc_v[2], self.rc_v[3],
                    self.rc_v[4], self.rc_v[5], self.rc_v[6],
                    self.rc_v[7], self.rc_v[8], self.rc_v[9])
            )

2) Current and target angles:
    'Current and target angles - r_c:{:.2f}; p_c:{:.2f}; r_t:{:.2f}; r_r:{:.2f}; r_y:{:.2f}

    
3) IMU values:
        log('IMU values. temp: "{:.2f}" '
            'acc x: "{:.2f}" y: "{:.2f}" z: "{:.2f}" '
            'gyro x: "{:.2f}" y: "{:.2f}" z: "{:.2f}"'.format(
                self.imu_v['temp'],
                acc['x'], acc['y'], acc['z'],
                gyro['x'], gyro['y'], gyro['z'])
        )

4) Motors after final tuning:        
    log('After final tuning. M1: "{:.2f}" M2: "{:.2f}" M3: "{:.2f}" M4: "{:.2f}"'.format(
        self.motor_values[1], self.motor_values[2],
        self.motor_values[3], self.motor_values[4]))

'''
import socket
import time
import random

# Server settings
IP = '127.0.0.1'
PORT = 4932
FREQUENCY = 1  # Hz
TIME_INTERVAL = 1 / FREQUENCY

# Simulate some data (you can replace this with actual sensor data)
def generate_rc_data():
    # rc_v = [random.randint(1000, 2000) for _ in range(10)]
    rc_v = [1500 + i for i in range(10)]
    # return 'RC inputs values. 0: "{}" 1: "{}" 2: "{}" 3: "{}" 4: "{}" 5: "{}" 6: "{}" 7: "{}" 8: "{}" 9: "{}"'.format(*rc_v)
    return ('RC inputs values - 0:{}; '
            '1:{}; 2:{}; 3:{}; '
            '4:{}; 5:{}; 6:{}; '
            '7:{}; 8:{}; 9:{}'.format(
                *rc_v))


def generate_target_angles():
    return 'Target angles - p:{:.2f}; r:{:.2f}; y:{:.2f}'.format(
        # random.uniform(-45, 45),
        # random.uniform(-45, 45),
        # random.uniform(-180, 180))
        0.1,
        0.2,
        0.3)

def generate_imu_values():
    return (
        'IMU values - t:{:.2f}; a_x:{:.2f}; a_y:{:.2f}; a_z:{:.2f}; '
        'g_x:{:.2f}; g_y:{:.2f}; g_z:{:.2f}'.format(
            26.6,
            0.32, -0.46, -9.74,
            0.1, 0.2, 0.3)
        # random.uniform(-10, 50),
        # random.uniform(-10, 10),
        # random.uniform(-10, 10),
        # random.uniform(-10, 10),
        # random.uniform(-10, 10),
        # random.uniform(-10, 10),
        # random.uniform(-10, 10)
    )

def generate_current_and_target_angles():
    return 'Current and target angles - r_c:{:.2f}; p_c:{:.2f}; r_t:{:.2f}; p_t:{:.2f}; y_t:{:.2f}'.format(
        -15.43,
        0.0,
        2.45,
        6.45,
        4.9)

def generate_motor_values():
    return 'Motor values are - M1:{:.2f}; M2:{:.2f}; M3:{:.2f}; M4:{:.2f}'.format(
        74.3,
        29.9,
        94.3,
        56.3
        # random.uniform(0, 100),
        # random.uniform(0, 100),
        # random.uniform(0, 100),
        # random.uniform(0, 100)
    )

# Create TCP server
def create_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    print(f"Server started on {IP}:{PORT}")
    return server_socket

def handle_client(client_socket):
    while True:
        rc_data = generate_rc_data()
        imu_values = generate_imu_values()
        current_and_target_angles = generate_current_and_target_angles()
        motor_values = generate_motor_values()

        message = f"{rc_data}\n{current_and_target_angles}\n{imu_values}\n{motor_values}\n"
        client_socket.sendall(message.encode())

        time.sleep(TIME_INTERVAL)

def main():
    server_socket = create_server()
    
    # Accept client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    try:
        handle_client(client_socket)
    except KeyboardInterrupt:
        print("Server is stopping...")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    main()
