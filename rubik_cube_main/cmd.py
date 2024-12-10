# File implementing the actual direct commands that are sent to and then executed
# by the Mindstorm bricks.

import ev3_dc as ev3
import struct

def reset(brick,port):
    cmd = b''.join((
        ev3.opOutput_Reset,
        ev3.LCX(0),  # LAYER
        ev3.LCX(port)  # NOS
    ))
    brick.send_direct_cmd(cmd, sync_mode=ev3.SYNC)

def run(brick, ports, pow):
    cmd = b''.join((
        ev3.opOutput_Start,
        ev3.LCX(0),  # LAYER
        ev3.LCX(ports),  # NOS
    ))
    cmd += b''.join((
        ev3.opOutput_Power,
        ev3.LCX(0),  # LAYER
        ev3.LCX(ports),  # NOS
        ev3.LCX(pow)  # POWER
    ))
    brick.send_direct_cmd(cmd)

# Read the tacho count of a motor
def cmd_tacho(port, var):
    return b''.join([
        ev3.opInput_Device, # 2byte
        ev3.GET_RAW, # 1byte
        ev3.LCX(0), # 1byte
        ev3.port_motor_input(port), # 1byte
        ev3.GVX(var) # 4byte
    ])

# 引数の角度だけモータを回転
def cmd_rotate(ports, deg):
    return b''.join([
        ev3.opOutput_Step_Power,
        ev3.LCX(0), # Specify chain layer number, [0 - 3]
        ev3.LCX(ports), # Output bit field, [0x00 – 0x0F]
        ev3.LCX(100 if deg > 0 else -100), # Power level, [-100 - 100]
        ev3.LCX(0), # Tacho pulses during ramp up
        ev3.LCX(abs(deg)), # Tacho pulses during continues run
        ev3.LCX(0), # Tacho pulses during ramp down
        ev3.LCX(1) # 0 Float 1 Break
    ])

# 時間制限
def cmd_rotate_t(ports, deg, time = 200):
    return b''.join([
        ev3.opOutput_Time_Power,
        ev3.LCX(0), # Specify chain layer number, [0 - 3]
        ev3.LCX(ports), # Output bit field, [0x00 – 0x0F]
        ev3.LCX(100 if deg > 0 else -100), # Power level, [-100 - 100]
        ev3.LCX(0), # Tacho pulses during ramp up
        ev3.LCX(time), # Tacho pulses during continues run
        ev3.LCX(0), # Tacho pulses during ramp down
        ev3.LCX(1) # 0 Float 1 Break
    ])

# Wait for any potentially ongoing rotations to complete.
def cmd_ready(ports):
    return b''.join([
        ev3.opOutput_Ready,
        ev3.LCX(0), # Specify chain layer number [0 - 3]
        ev3.LCX(ports) # Output bit field [0x00 – 0x0F]
    ])

# Compute target tacho count for waiting
def cmd_waitdeg_target(deg, waitport, waitdeg, tarvar):
    return cmd_tacho(waitport, tarvar) + b''.join([
        ev3.opAdd32,
        ev3.GVX(tarvar),
        ev3.LCX(waitdeg if deg > 0 else -waitdeg),
        ev3.GVX(tarvar)
    ])

def cmd_waitdeg_wait(deg, waitport, tarvar, waitvar):
    return cmd_tacho(waitport, waitvar) + b''.join([
        ev3.opJr_Lt32 if deg > 0 else ev3.opJr_Gt32,
        ev3.GVX(waitvar),
        ev3.GVX(tarvar),
        ev3.LCX(-9)
    ])

def some_port(ports):
    return 1 << ((ports & -ports).bit_length() - 1)

def lift(brick, ports, deg, waitdeg = 0):
    waitport = some_port(ports)
    cmd = cmd_ready(ports)
    cmd += cmd_waitdeg_target(deg, waitport, waitdeg, 0)
    cmd += cmd_rotate(ports, deg)
    brick.send_direct_cmd(cmd)

# 単体操作
def rotate(brick, ports, deg, waitdeg):
    waitport = some_port(ports)
    cmd = cmd_ready(ports)
    cmd += cmd_waitdeg_target(deg, waitport, waitdeg, 0)
    cmd += cmd_rotate(ports, deg)
    cmd += cmd_waitdeg_wait(deg, waitport, 0, 4)
    brick.send_direct_cmd(cmd, global_mem=8)

# 単体操作_時間
def rotate_t(brick, ports, deg):
    cmd = cmd_ready(ports)
    cmd += cmd_rotate_t(ports, deg)
    brick.send_direct_cmd(cmd, sync_mode=ev3.SYNC)

# 同時操作
def rotate1(brick, ports1, ports2, deg1, deg2, waitdeg):
    waitport = some_port(ports2)
    cmd = cmd_ready(ports1 + ports2)
    cmd += cmd_waitdeg_target(deg2, waitport, waitdeg, 0)
    cmd += cmd_rotate(ports1, deg1)
    cmd += cmd_rotate(ports2, deg2)
    cmd += cmd_waitdeg_wait(deg2, waitport, 0, 4)
    brick.send_direct_cmd(cmd, global_mem=8)

# アーム操作
def arm_rotate(brick, ports, deg):
    cmd = cmd_ready(ports)
    cmd += cmd_rotate(ports, deg)
    brick.send_direct_cmd(cmd, global_mem=8, sync_mode=ev3.SYNC)


# Perform an axial move where one side is a half-turn and the other a quarter-turn.
# In this case we want to start the latter turn a little later so that they both
# end jointly and are thus automatically aligned by the next move.
def rotate2(brick, ports1, ports2, deg1, deg2, waitdeg1, waitdeg2):
    waitport = some_port(ports1)
    cmd = cmd_ready(ports1 + ports2)
    cmd += cmd_waitdeg_target(deg1, waitport, waitdeg1, 0)
    cmd += cmd_waitdeg_target(deg1, waitport, waitdeg2, 4)
    cmd += cmd_rotate(ports1, deg1)
    cmd += cmd_waitdeg_wait(deg1, waitport, 0, 8)
    cmd += cmd_rotate(ports2, deg2)
    cmd += cmd_waitdeg_wait(deg1, waitport, 4, 8)
    brick.send_direct_cmd(cmd, global_mem=12)

def stop(brick, port):
    cmd = b''.join((
        ev3.opOutput_Stop,
        ev3.LCX(0),  # LAYER
        ev3.LCX(port),  # NOS
        ev3.LCX(0)  # BRAKE - no
    ))
    brick.send_direct_cmd(cmd)

def is_pressed(brick, port):
    cmd = b''.join([
        ev3.opInput_Read,
        ev3.LCX(0),
        port,
        ev3.LCX(16),
        ev3.LCX(0),
        ev3.GVX(0) 
    ])
    recv = struct.unpack('<b', brick.send_direct_cmd(cmd, global_mem=1))
    return recv[0] > 0

def read_color(brick, port):
    cmd = b''.join((
        ev3.opInput_Device,  # operation
        ev3.READY_RAW,  # CMD
        ev3.LCX(0),  # LAYER
        port,  # NO
        ev3.LCX(29),  # TYPE (EV3-Color)
        ev3.LCX(0),  # MODE (Color)
        ev3.LCX(1),  # VALUES
        ev3.GVX(0)  # VALUE1 (output)
    ))
    recv = struct.unpack('<b', brick.send_direct_cmd(cmd, global_mem=1))
    return recv[0]

def color_off(brick, port):
    cmd = b''.join((
        ev3.opInput_Device,  # operation
        ev3.READY_SI,  # CMD
        ev3.LCX(0),  # LAYER
        port,  # NO
        ev3.LCX(29),  # TYPE (EV3-Color)
        ev3.LCX(0),  # MODE (Color)
        ev3.LCX(1),  # VALUES
        ev3.GVX(0)  # VALUE1 (output)
    ))
    recv = struct.unpack('<b', brick.send_direct_cmd(cmd, global_mem=1))
    return recv[0]
