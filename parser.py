#!/usr/bin/env python3

f = open('test.cc', 'r')
buf = []


for line in f:
    if '/**' in line:
        if len(line) is not 4:
            line = list(line)
            buf.append(''.join(line[0:3]) + '\n')
            buf.append(''.join(line[4:]))
        else:
            buf.append(line)

        for line2 in f:
            buf.append(line2)
            if "*/" in line2: break

    buf.append(line)
print(type(buf))
# r = open('result.cc', 'w')
# for i in buf:
#     r.write(i)

