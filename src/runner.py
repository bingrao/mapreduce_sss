# http://blog.sina.com.cn/s/blog_9f0384e70101gj8x.html

p = random_prime(2 ^ 12)
p = 67
Zp = GF(p)
IFtest = true
# number of clouds
n_clouds = 10

# to store vectorlist for mapping from alphabet to vectors
vectorlist = matrix(53)
alphabetlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
for i in range(53):
	vectorlist[i, i] = 1


# generate n randome numbers, not repeated
def GenR(n, Zp):
	l_xs = []
	tem = Zp.random_element()
	while tem == 0:
		tem = Zp.random_element()


l_xs.append(tem)
while len(l_xs) < n:
	tem = Zp.random_element()
	while tem == 0:
		tem = Zp.random_element()
	if FindinList(tem, l_xs) < 0:
		l_xs.append(tem)
return l_xs


# find a number in a list
# not find, return -1
def FindinList(tem, lxs):
	lenlist = len(lxs)
	ret = -1
	for x in range(lenlist):
		if lxs[x] == tem:
			ret = x
			break
	return ret


# input:prime number, order
# output a efficiency list of a polynomial
def GenPolynomial(p, n_Polynomialorder):
	Zp = GF(p)


n_efficiency = []
for i in range(n_Polynomialorder + 1):
	n_efficiency.append(Zp.random_element())
return n_efficiency


# input: order, efficiency, xvlaues
# output: Result
def EvalPolynomial(n_Polynomialorder, n_efficiency, n_Values):
	result = 0
	for i in range(n_Polynomialorder + 1):
		result = result + n_efficiency[i] * n_Values ^ i
	# print 'n_values=',n_Values,'r=',result
	return result


# input: xlabel, ylabel, order of the polynomial
# output a polynomial with n_Polynomialorder degree.
def interpolation(xs, ys, n_order):
	pi(x) = prod(x - i for i in xs)
	# print pi(x)
	pid(x) = diff(pi(x), x)
	# print pid(x)
	P(x) = sum(pi(x) / (x - i) / pid(i) * j for (i, j) in zip(xs, ys))
	f = P(x).collect(x)
	return f


# input: alphabet
# ouput: vector
# 53 symbols to vectors. a-z,A-Z,and blank.
def MapAlphabetToVector(x):
	i = alphabetlist.index(x)
	return vectorlist[i]


# input: number in Zp, number of clouds, order of the polynomial
# ouput: vector
# function
def secretshare(y, n_clouds, n_order):
	shares = []
	f_poly = GenPolynomial(p, n_order)
	f_poly[0] = y
	# print f_poly
	for x in range(n_clouds):
		resultValue = EvalPolynomial(n_order, f_poly, l_xs[x])
		shares.append(resultValue)
	# print "def secretshare(y,n_clouds,n_order):",shares
	return shares


print
'main program\n', '----------------------------------------------------------------------'
# main program

# genearte n_clouds x values for each cloud
l_xs = []
l_xs = GenR(n_clouds, Zp)
if IFtest: print
'The finite filed we are using: \n Zp=', Zp
if IFtest: print
'cloud numbers: ', len(l_xs)
if IFtest: print
'x values for each cloud:', l_xs
# input one file to share
FiletoBestored = 'Alice Love Bob  '
if IFtest: print
'file stream to be searched:', FiletoBestored
# Map File to VectorList
vector = []
# for temporary store vector
l_Filshares = []
# for one file in one cloud, one row for one cloud. (for example 10 clouds)
# in each row, every cell for one alphabet (for example each cell consists of 53 elements)
for x in FiletoBestored:
	l_Filshares.append([])
for x in FiletoBestored:
	vector = MapAlphabetToVector(x)
	# print vector
	# secret share each vector
	l_y_vectorshares = []  # for one vector,or for one symbol
	for xx in range(n_clouds):
		l_y_vectorshares.append([])
# if IFtest: print 'for one symbol'; print l_y_vectorshares
shares = []  # for one element (0 or 1)
for y in vector:
	# print 'y=',y
	shares = secretshare(y, n_clouds, 1);  # one degree sharing, so we need 1 here.
	# for xx in range(n_clouds):
	# if IFtest: print 'l_y_vectorshares[xx]',xx; print len(l_y_vectorshares[xx])
	for xx in range(n_clouds):
		l_y_vectorshares[xx].append(shares[xx])
	# send to clouds
# transfer data in l_y_vectorshares to l_Filshares
for xx in range(n_clouds):
	l_Filshares[xx].append(l_y_vectorshares[xx])
# file are sent to l_Filshares;
# l_Filshares[x] for cloud x
if IFtest:
	print
	'distribute file ending...';
	print
	'-----------------------------------'
# Generate automaton and secret share it between n clouds
# inut one word to search
# here we give the word "Love"
if IFtest:
	print
	'Generate AA now';
n_node = 5
l_Node = []
l_NodesharesforC = []
for i in range(n_node):
	l_Node.append(0)

# set initial value for each node
l_Node[0] = 1;  # for 'L'
l_Node[1] = 0;  # for 'o'
l_Node[2] = 0;  # for 'v'
l_Node[3] = 0;  # for 'e'
l_Node[4] = 0;
# set positon for the word 'Love'
n_1to2 = alphabetlist.index('L');  # it is 11
n_2to3 = alphabetlist.index('o');  # it is 40
n_3to4 = alphabetlist.index('v');  # it is 47
n_4to5 = alphabetlist.index('e');  # it is 30

# set initial cell for n_clouds clouds
for xx in range(n_clouds):
	l_NodesharesforC.append([])
# secret share AA
# each share for x cloud is stored in l_NodesharesforC[x]
for i in range(n_node):
	shares = secretshare(l_Node[i], n_clouds, i + 2)
	for xx in range(n_clouds):
		l_NodesharesforC[xx].append(shares[xx])
# print l_NodesharesforC
if IFtest: print
"original AA:N0,N1,N2,N3,N4", l_Node
if IFtest:
	print
	'Generate AA ending...';
	print
	'---------------------------------------'

# todo upate AA in clouds.
if IFtest:
	print
	'Updating AA now';
# each cloud will update AA for theirselves
FileLen = len(l_Filshares[1])  # it is 14 for 'Alice Love Bob'
# print l_Filshares[9][13][52]
for i in range(FileLen):
	# for each symbol in file stream
	for xx in range(n_clouds):
		l_NodesharesforC[xx][4] = l_NodesharesforC[xx][4] + l_NodesharesforC[xx][3] * l_Filshares[xx][i][n_4to5]
		l_NodesharesforC[xx][3] = l_NodesharesforC[xx][2] * l_Filshares[xx][i][n_3to4]
		l_NodesharesforC[xx][2] = l_NodesharesforC[xx][1] * l_Filshares[xx][i][n_2to3]
		l_NodesharesforC[xx][1] = l_NodesharesforC[xx][0] * l_Filshares[xx][i][n_1to2]

if IFtest:
	print
	'Upate AA ending...';
	print
	'--------------------------------------------'
# todo Reconstruct AA
if IFtest:
	print
	'Reconstruct AA now';
# From shares got from clouds
# which are stored in list l_NodesharesforC
n_node = 5
for i in range(n_node):
	l_Node[i] = 0

# the first node
# lxs=[]
# lys=[]
# f_poly=interpolation(xs,ys,2)
# l_Node[0]=f_poly(0)
for xx in range(5):
	lxs = []
	lys = []
	# print '--',lxs,lys
	for y in range(xx + 3):
		lxs.append(l_xs[y])
		lys.append(l_NodesharesforC[y][xx])
	# print '===',xx,y,lxs,lys
f_poly = interpolation(lxs, lys, xx + 2)
# g=f_poly.polynomial(ZZ)
lenofpoly = len(f_poly)
print
'the reconstructed polynomial:', f_poly
if lenofpoly > 0:
	l_Node[xx] = f_poly(0)
else:
	l_Node[xx] = 0

# the second node

if IFtest: print
"Reconstruct AA:N0,N1,N2,N3,N4", l_Node
if IFtest:
	print
	'Reconstruct AA ending...';
	print
	'-------------------------------------'
