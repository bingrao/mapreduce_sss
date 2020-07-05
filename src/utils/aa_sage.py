#
# This version is implemented based sage math, but we do not this one.
# http://blog.sina.com.cn/s/blog_9f0384e70101gj8x.html
import logging
import sage.all
from sage.arith.misc import random_prime
from sage.rings.finite_rings.all import GF


logging.basicConfig(level=logging.DEBUG)

p = random_prime(2 ** 12)
Zp = GF(p)  # Finite Field of size 67

# to store vectorlist for mapping from alphabet to vectors
vectorlist = matrix(53)
alphabetlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
for i in range(53):
    vectorlist[i, i] = 1


# input: alphabet
# ouput: vector
# 53 symbols to vectors. a-z,A-Z,and blank.
def MapAlphabetToVector(x):
    i = alphabetlist.index(x)
    return vectorlist[i]


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


# generate n randome numbers, not repeated
def GenR(n, Zp):
    l_xs = []
    tem = Zp.random_element()  # Get next primary number in FP
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
def EvalPolynomial(n_Polynomialorder, n_efficiency, xvlaues):
    result = 0
    for i in range(n_Polynomialorder + 1):
        result = result + n_efficiency[i] * xvlaues ^ i
    return result


def secretshare(y, n_clouds, n_order, l_xs):
    shares = []
    f_poly = GenPolynomial(p, n_order)
    f_poly[0] = y
    for x in range(n_clouds):
        resultValue = EvalPolynomial(n_order, f_poly, l_xs[x])
        shares.append(resultValue)
    return shares


# input: xlabel, ylabel, order of the polynomial
# output a polynomial with n_Polynomialorder degree.
def interpolation(xs, ys, n_order):
    pi(x) = prod(x-i for i in xs)
    #print pi(x)
    pid(x) = diff(pi(x),x)
    #print pid(x)
    P(x) = sum(pi(x)/(x-i)/pid(i)*j for (i,j) in zip(xs,ys))
    f=P(x).collect(x)
    return f


logging.info('main program\n')
logging.info('----------------------------------------------------------------------')
# main program

# number of clouds
n_clouds = 10
# genearte n_clouds x values for each cloud as an identification of an clound
l_xs = []
l_xs = GenR(n_clouds, Zp)
logging.info(f"The finite filed we are using: Zp = {Zp}")
logging.info(f"cloud numbers: {len(l_xs)}")
logging.info(f"x values for each cloud: {l_xs}")

# input one file to share
FiletoBestored = 'Alice Love Bob'.strip()
logging.info(f"file stream to be searched: {FiletoBestored}")

# Map FiletoBestored to VectorList
vector = []

# for temporary store vector
l_Filshares = []  # Size n_clouds * seq_len, a cell is a list of shares with size of 53
# for one file in one cloud, one row for one cloud. (for example 10 clouds)
# in each row, every cell for one alphabet (for example each cell consists of 53 elements)

for x in range(n_clouds):
    l_Filshares.append([])

for x in FiletoBestored:
    vector = MapAlphabetToVector(x)  # Get a vector representation for a char x

    # secret share each vector
    # for one vector,or for one symbol
    # Size: n_clouds = 10 * vector_size = 53. For each row, it is a collection of
    # secret shares of input char x for a specific party.
    # For each column, it is a all list of secret shares of a bit in the vector
    l_y_vectorshares = []
    for xx in range(n_clouds):
        l_y_vectorshares.append([])

    shares = []  # for one element (0 or 1)
    for y in vector:
        shares = secretshare(y, n_clouds, 1, l_xs)  # one degree sharing, so we need 1 here.
        for xx in range(n_clouds):
            l_y_vectorshares[xx].append(shares[xx])

    # send to clouds
    # transfer data in l_y_vectorshares to l_Filshares
    for xx in range(n_clouds):
        l_Filshares[xx].append(l_y_vectorshares[xx])

logging.info('distribute file ending...')
logging.info('-----------------------------------')

# Generate automaton and secret share it between n clouds
# inut one word to search
# here we give the word "Love"
logging.info('Generate AA now')

n_node = 5
l_Node = []
for i in range(n_node):
    l_Node.append(0)

# set initial value for each node
l_Node[0] = 1  # for 'L'
l_Node[1] = 0  # for 'o'
l_Node[2] = 0  # for 'v'
l_Node[3] = 0  # for 'e'
l_Node[4] = 0

# set positon for the word 'Love'
n_1to2 = alphabetlist.index('L')  # it is 11
n_2to3 = alphabetlist.index('o')  # it is 40
n_3to4 = alphabetlist.index('v')  # it is 47
n_4to5 = alphabetlist.index('e')  # it is 30

logging.info(f"Index [L -> {n_1to2}], [o -> {n_2to3}], [v -> {n_3to4}], [e -> {n_4to5}]")

l_NodesharesforC = []  # Size: n_clouds * nums_nodes
# set initial cell for n_clouds clouds
for xx in range(n_clouds):
    l_NodesharesforC.append([])

# secret share AA
# each share for x cloud is stored in l_NodesharesforC[x]
for i in range(n_node):
    shares = secretshare(l_Node[i], n_clouds, i + 2, l_xs)
    for xx in range(n_clouds):
        l_NodesharesforC[xx].append(shares[xx])

logging.info(f"original AA:N0,N1,N2,N3,N4 -> {l_Node}")
logging.info(f"Generate AA ending...")
logging.info("---------------------------------------")

# todo upate AA in clouds.
logging.info("Updating AA now")

# each cloud will update AA for theirselves
FileLen = len(l_Filshares[0])  # it is 14 for 'Alice Love Bob'

for i in range(FileLen):
    # for each symbol in file stream
    for xx in range(n_clouds):
        l_NodesharesforC[xx][4] = l_NodesharesforC[xx][4] + l_NodesharesforC[xx][3] * l_Filshares[xx][i][n_4to5]
        l_NodesharesforC[xx][3] = l_NodesharesforC[xx][2] * l_Filshares[xx][i][n_3to4]
        l_NodesharesforC[xx][2] = l_NodesharesforC[xx][1] * l_Filshares[xx][i][n_2to3]
        l_NodesharesforC[xx][1] = l_NodesharesforC[xx][0] * l_Filshares[xx][i][n_1to2]

logging.info("Upate AA ending...")
logging.info("--------------------------------------------")

# todo Reconstruct AA
logging.info("Reconstruct AA now")
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
    for y in range(xx + 3):
        lxs.append(l_xs[y])
        lys.append(l_NodesharesforC[y][xx])
    f_poly = interpolation(lxs, lys, xx + 2)
    lenofpoly = len(f_poly)
    logging.info("the reconstructed polynomial: {f_poly}")
    if lenofpoly > 0:
        l_Node[xx] = f_poly(0)
    else:
        l_Node[xx] = 0

# the second node

logging.info("Reconstruct AA:N0,N1,N2,N3,N4 -> {l_Node}")
logging.info("Reconstruct AA ending...")
logging.info("-------------------------------------")
