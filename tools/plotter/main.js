const fs = require('fs');
const net = require('net');
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app_plots = express();
const server_plots = http.createServer(app_plots);
const io_plots = new Server(server_plots);

const app_gl = express();
const server_gl = http.createServer(app_gl);
const io_gl = new Server(server_gl);

// Log file path
const logFilePath = '/tmp/quad_logs.txt';

function logToFileAndConsole(...args) {
    const logMessage = args.join(' ') + '\n';
    console.log(...args);
    fs.appendFileSync(logFilePath, logMessage);
}

// how js communicate with tcp server
// Skip the first two default arguments
const args = process.argv.slice(2);
// Default to '127.0.0.1' if not provided
const TCP_IP = args[0] || '127.0.0.1';
const TCP_PORT = 4932;

app_plots.use(express.static('public_plots'));
app_gl.use(express.static('public_gl'));

// TCP client logic
const client = new net.Socket();
client.connect(TCP_PORT, TCP_IP, () => {
    logToFileAndConsole("Connected to the TCP server");
    client.write("Hello server");
});

client.on('data', (data) => {
    const parsedData = parseData(data.toString());
    // Send parsed data to the web clients
    io_plots.emit('tcp-data', parsedData);
    io_gl.emit('tcp-data', parsedData);
});

client.on('close', () => {
    logToFileAndConsole("Connection to TCP server closed");
});

client.on('error', (err) => {
    console.error('Connection error:', err.message);
});

let prevTimestamp = null;

// Parse the incoming data
function parseData(data) {
    const parsed = {};
    const lines = data.split("\n");



    lines.forEach(line => {
        if (line.startsWith('RC inputs values - ')) {
            parsed.rc_inputs = {};
            parsed.frequency = {};
            const rc_inputs = line.split(' - ')[1]?.split('; ');

             // Get the current timestamp
            const currentTimestamp = new Date().getTime();
            // If it's not the first time, calculate the time difference
            if (prevTimestamp !== null) {
                // Time difference in seconds
                const timeDifference = (currentTimestamp - prevTimestamp) / 1000;
                parsed.frequency["frequency"] = 1 / timeDifference;
                // logToFileAndConsole(
                //     `[${new Date().toISOString()}]`,
                //     `Frequency: ${parsed.frequency.toFixed(2)} Hz`
                // );
            }

            prevTimestamp = currentTimestamp;
            if (rc_inputs && Array.isArray(rc_inputs)) {
                rc_inputs.forEach(item => {
                    const [key, value] = item.split(':');
                    if (key && value !== undefined) {
                        parsed.rc_inputs[key] = parseFloat(value);
                    }
                });
            }
            logToFileAndConsole(
                `[${new Date().toISOString()}]`,
                `RC inputs: ${JSON.stringify(parsed.rc_inputs, null, 2)}`
            );

        } else if (line.startsWith('Current and target angles - ')) {
            parsed.current_and_target_angles = {};
            const current_and_target_angles = line.split(' - ')[1]?.split('; ');

            if (current_and_target_angles && current_and_target_angles.length >= 5) {
                ['roll_cur', 'pitch_cur', 'roll_tar', 'pitch_tar', 'yaw_tar'].forEach((angle, index) => {
                    const anglePair = current_and_target_angles[index]?.split(':');
                    if (anglePair && anglePair.length === 2) {
                        parsed.current_and_target_angles[angle] = parseFloat(anglePair[1]);

                    }
                });
                logToFileAndConsole(
                    `[${new Date().toISOString()}]`,
                    `Current and target angles: ${JSON.stringify(parsed.current_and_target_angles, null, 2)}`
                );
            }
        } else if (line.startsWith('IMU values - ')) {
            parsed.imu_values = {};
            const imu_values = line.split(' - ')[1]?.split('; ');

            if (imu_values && imu_values.length >= 6) {
                ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'].forEach((imu, index) => {
                    const imuPair = imu_values[index]?.split(':');
                    if (imuPair && imuPair.length === 2) {
                        parsed.imu_values[imu] = parseFloat(imuPair[1]);
                    }
                });
                logToFileAndConsole(
                    `[${new Date().toISOString()}]`,
                    `IMU values: ${JSON.stringify(parsed.imu_values, null, 2)}`
                );
            }

        } else if (line.startsWith('Motor values are - ')) {
            parsed.motor_values = {};
            const motor_values = line.split(' - ')[1]?.split('; ');

            if (motor_values && motor_values.length >= 4) {
                ['M1', 'M2', 'M3', 'M4'].forEach((motor, index) => {
                    const motorPair = motor_values[index]?.split(':');
                    if (motorPair && motorPair.length === 2) {
                        parsed.motor_values[motor] = parseFloat(motorPair[1]);
                    }
                });
                logToFileAndConsole(
                    `[${new Date().toISOString()}]`,
                    `Target motor values: ${JSON.stringify(parsed.motor_values, null, 2)}`
                );
            }
        }
    });

    return parsed;
}

// Start the web servers

server_plots.listen(3000, () => {
    logToFileAndConsole('Server with plots is running on http://localhost:3000');
});

server_gl.listen(3001, () => {
    logToFileAndConsole('Server with gl is running on http://localhost:3001');
});
