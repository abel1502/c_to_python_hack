#include <vector>
#include <algorithm>
#include <cstdlib>
#include <iostream>
 
using namespace std;

typedef     long long             ll;
typedef     pair<int, int>        pii;
typedef     pair<ll, ll>          pll;

#define     all(a)                a.begin(), a.end()
#define     fi                    first
#define     se                    second

const int MAX_N = 2e5 + 5;

int up[MAX_N][20];
ll sum[MAX_N][20];
int root[MAX_N];
vector<int> mem[MAX_N];
vector<pii> adj[MAX_N];
int dep[MAX_N];
int n, q;
int sumPrevQuery = 0;

int findRoot(int u) {
	if (root[u] == u) {
		return u;
	}
	return root[u] = findRoot(root[u]);
}

void dfs(int u) {
	for (pii it : adj[u]) {
		int v = it.fi;
		int w = it.se;
		if (v != up[u][0]) {
			up[v][0] = u;
			sum[v][0] = w;
			dep[v] = dep[u] + 1;
			dfs(v);
		}
	}
}

void unionSet(int u, int v, int w) {
	int rootU = findRoot(u);
	int rootV = findRoot(v);
	if ((int) mem[rootU].size() < (int) mem[rootV].size()) {
		swap(u, v);
		swap(rootU, rootV);
	} // mem trong u > mem trong v

	// gop cay
	root[rootV] = rootU;
	for (int i : mem[rootV]) {
		mem[rootU].push_back(i);
	}

	// noi cay
	dep[v] = dep[u] + 1;
	up[v][0] = u;
	sum[v][0] = w;
	dfs(v);
	// update adj
	adj[u].push_back({v, w});
	adj[v].push_back({u, w});
	// update rmq
	for (int i : mem[rootV]) {
		for (int j = 1; j < 20; j++) {
			up[i][j] = -1;
		}
	}
	for (int j = 1; j < 20; j++) {
		for (int i : mem[rootV]) {
			if (~up[i][j - 1]) {
				up[i][j] = up[up[i][j - 1]][j - 1];
				sum[i][j] = sum[i][j - 1] + sum[up[i][j - 1]][j - 1];
			}
		}
	}
}

ll getSum(int u, int v) {
	int rootU = findRoot(u);
	int rootV = findRoot(v);
	if (rootU != rootV) {
		return -1;
	}

	ll res = 0;
	if (dep[u] != dep[v]) {
		if (dep[u] < dep[v]) {
			swap(u, v);
		}
		int k = dep[u] - dep[v];
		for (int i = 0; (1 << i) <= k; i++) {
			if (k >> i & 1) {
				res += sum[u][i];
				u = up[u][i];
			}
		}
	}

	if (u == v) {
		return res;
	}

	for (int i = __lg(dep[u]); ~i; i--) {
		if (~up[u][i] && ~up[v][i] && up[u][i] != up[v][i]) {
			res += sum[u][i] + sum[v][i];
			u = up[u][i];
			v = up[v][i];
		}
	}

	return res + sum[u][0] + sum[v][0];
}

signed main() {
	ios_base::sync_with_stdio(false);
	cin.tie(nullptr);

	cin >> n >> q;

	for (int i = 1; i <= n; i++) {
		root[i] = i;
		mem[i].push_back(i);
		for (int j = 0; j < 20; j++) {
			up[i][j] = -1;
		}
	}

	while (q--) {
		int type, i, j;
		cin >> type;
		cin >> i >> j;

		i = (sumPrevQuery + i + n) % n + 1;
		j = (sumPrevQuery + j + n) % n + 1;

		if (type == 1) {
			ll c;
			cin >> c;
			unionSet(i, j, c);
			continue;
		}

		if (type == 2) {
			ll ans = getSum(i, j);
			cout << ans << '\n';
			sumPrevQuery = (ans + 1ll * n * n) % n;
			continue;
		}
	}

	return 0;
}
