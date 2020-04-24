from subprocess import Popen, PIPE

input_cmd = "cat /home/jacroute/Bureau/IMG_20200326_091927876.jpg"
output_cmd = "tee /dev/null"

print("%s --> %s" % (input_cmd, output_cmd))
bytes_written = 0
with Popen(output_cmd.split(), stdin=PIPE, stderr=PIPE) as output:
    with Popen(input_cmd.split(), stdout=PIPE, stderr=PIPE) as input:
        while True:
            buffer = input.stdout.read1()
            if len(buffer) == 0:
                break
            bytes_written += len(buffer)
            print('Write %s bytes' % len(buffer))
            output.stdin.write(buffer)
        if input.poll() is not None:
            output.stdin.close()
            output.wait()
            print("%s bytes written" % bytes_written)

print("Done")