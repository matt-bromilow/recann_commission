def load(fname):
    import csv
    #initial content
    with open('mycsvfile.csv','w') as f:
        f.write('a,b,c\n1,1,1\n') # TRAILING NEWLINE

    with open('mycsvfile.csv','a',newline='') as f:
        writer=csv.writer(f)
        writer.writerow([0,0,0])
        writer.writerow([0,0,0])
        writer.writerow([0,0,0])

    with open('mycsvfile.csv') as f:
        print(fname)

