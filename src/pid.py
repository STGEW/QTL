
# complementary filter
# 
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0
    
    def reset(self):
        self.prev_error = 0.0
        self.integral = 0.0

    def update(self, target_value, current_value, dt):
        error = target_value - current_value
        # self.integral += error * dt
        # derivative = (error - self.prev_error) / dt if dt > 0 else 0

        # output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        
        output = self.kp * error
        

        return output
