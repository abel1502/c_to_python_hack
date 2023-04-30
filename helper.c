#include <stdint.h>
#include <stddef.h>


#pragma region 'Imported' functions
#define IMPORTED __attribute__((section(".libc-imp")))

IMPORTED void *(*volatile malloc)(size_t size) = NULL;
IMPORTED void *(*volatile realloc)(void *ptr, size_t size) = NULL;
IMPORTED void (*volatile free)(void *ptr) = NULL;
IMPORTED void *(*volatile memcpy)(void *dest, void *src, size_t count) = NULL;
// #define memcpy __builtin_memcpy
IMPORTED int (*volatile printf)(const char *format, ...) = NULL;
IMPORTED int (*volatile scanf)(const char *format, ...) = NULL;

#undef IMPORTED
#pragma endregion


#pragma region Vector but awesome
struct vector {
    void *data;
    size_t size;
    size_t capacity;
};


#define VECTOR_NEW(TYPE, CAPACITY) (struct vector){     \
    .data = malloc(sizeof(TYPE) * (CAPACITY)),          \
    .size = 0,                                          \
    .capacity = (CAPACITY),                             \
}


#define VECTOR_ENSURE(VECTOR, TYPE, CAPACITY)           \
    while ((VECTOR).capacity < (CAPACITY)) {            \
        (VECTOR).capacity *= 2;                         \
        (VECTOR).data = realloc(                        \
            (VECTOR).data,                              \
            sizeof(TYPE) * (VECTOR).capacity            \
        );                                              \
    }


#define VECTOR_PUSH_BACK(VECTOR, TYPE, VALUE) do {      \
    VECTOR_ENSURE(VECTOR, TYPE, (VECTOR).size + 1);     \
    ((TYPE *)(VECTOR).data)[(VECTOR).size++] = (VALUE); \
} while (0)


#define VECTOR_EXTEND(VECTOR, TYPE, OTHER) do {         \
    VECTOR_ENSURE(VECTOR, TYPE,                         \
                  (VECTOR).size + (OTHER).size);        \
    memcpy(                                             \
        (TYPE *)(VECTOR).data + (VECTOR).size,          \
        (OTHER).data,                                   \
        sizeof(TYPE) * (OTHER).size                     \
    );                                                  \
    (VECTOR).size += (OTHER).size;                      \
} while (0)


#define VECTOR_ITEM(VECTOR, TYPE, INDEX)                \
    ((TYPE *)(VECTOR).data)[INDEX]


#define VECTOR_FREE(VECTOR) do {                        \
    free((VECTOR).data);                                \
    (VECTOR).data = NULL;                               \
    (VECTOR).size = 0;                                  \
    (VECTOR).capacity = 0;                              \
} while (0)
#pragma endregion


#pragma region 2D array
#define NEW_2D(TYPE) \
    (TYPE *)malloc(sizeof(TYPE) * nodes_cnt * LOG_NODES_CNT)


#define ITEM_2D(ARR, LEVEL, NODE) \
    ARR[(LEVEL) * nodes_cnt + (NODE)]


#define FREE_2D(ARR) \
    free(ARR)
#pragma endregion


#pragma region Input
inline int32_t read_int32() {
    int32_t value;
    scanf("%d", &value);
    return value;
}


inline int64_t read_int64() {
    int64_t value;
    scanf("%lld", &value);
    return value;
}
#pragma endregion


#pragma region Consts and globals
#define LOG_NODES_CNT 20


int32_t nodes_cnt, ops_cnt;

int32_t *dsu_parents;
struct vector *dsu_items;

int32_t *depths;
int64_t *costs;
int32_t *nexts;
struct vector *neighbours;


struct neighbour {
    int32_t node;
    int64_t cost;
};
#pragma endregion


#pragma region DSU
void dsu_init() {
    dsu_parents = malloc(sizeof(*dsu_parents) * nodes_cnt);
    dsu_items = malloc(sizeof(*dsu_items) * nodes_cnt);

    for (int32_t i = 0; i < nodes_cnt; ++i) {
        dsu_parents[i] = i;
        dsu_items[i] = VECTOR_NEW(int32_t, 1);
        VECTOR_PUSH_BACK(dsu_items[i], int32_t, i);
    }
}


void dsu_free() {
    free(dsu_parents);
    dsu_parents = NULL;

    for (int32_t i = 0; i < nodes_cnt; ++i) {
        VECTOR_FREE(dsu_items[i]);
    }
    free(dsu_items);
    dsu_items = NULL;
}


int32_t dsu_root(int32_t node) {
    if (dsu_parents[node] == node) {
        return node;
    }

    return dsu_parents[node] = dsu_root(dsu_parents[node]);
}


struct dsu_join_result {
    int32_t node_a;
    int32_t node_b;
    int32_t root_a;
    int32_t root_b;
};

struct dsu_join_result dsu_join(int32_t node_a, int32_t node_b) {
    int32_t root_a = dsu_root(node_a);
    int32_t root_b = dsu_root(node_b);

    if (root_a == root_b) {
        return (struct dsu_join_result){
            .node_a = node_a,
            .node_b = node_b,
            .root_a = root_a,
            .root_b = root_b,
        };
    }

    if (dsu_items[root_a].size < dsu_items[root_b].size) {
        int32_t tmp = node_a;
        node_a = node_b;
        node_b = tmp;

        tmp = root_a;
        root_a = root_b;
        root_b = tmp;
    }

    dsu_parents[root_b] = root_a;

    struct vector *items_a = &dsu_items[root_a];
    struct vector *items_b = &dsu_items[root_b];

    VECTOR_EXTEND(*items_a, int32_t, *items_b);

    return (struct dsu_join_result){
        .node_a = node_a,
        .node_b = node_b,
        .root_a = root_a,
        .root_b = root_b,
    };
}
#pragma endregion


#pragma region Task API
void dfs_init(int32_t parent, int32_t node, int64_t cost) {
    depths[node] = depths[parent] + 1;
    ITEM_2D(nexts, 0, node) = parent;
    ITEM_2D(costs, 0, node) = cost;

    struct neighbour *end = (struct neighbour *)neighbours[node].data + neighbours[node].size;
    for (struct neighbour *cur = (struct neighbour *)neighbours[node].data; cur != end; ++cur) {
        if (cur->node == parent) {
            continue;
        }

        dfs_init(node, cur->node, cur->cost);
    }
}


void add_edge(int32_t node_a, int32_t node_b, int64_t cost) {
    struct dsu_join_result join_result = dsu_join(node_a, node_b);

    dfs_init(join_result.node_a, join_result.node_b, cost);

    struct vector *neighbours_a = &neighbours[join_result.node_a];
    struct vector *neighbours_b = &neighbours[join_result.node_b];
    VECTOR_PUSH_BACK(
        *neighbours_a,
        struct neighbour,
        ((struct neighbour){.node = join_result.node_b, .cost = cost})
    );
    VECTOR_PUSH_BACK(
        *neighbours_b,
        struct neighbour,
        ((struct neighbour){.node = join_result.node_a, .cost = cost})
    );

    int32_t *nodes = dsu_items[join_result.root_a].data;
    const size_t given_nodes_cnt = dsu_items[join_result.root_a].size;

    for (int32_t level = 1; level < LOG_NODES_CNT; ++level) {
        for (size_t i = 0; i < given_nodes_cnt; ++i) {
            int32_t node = nodes[i];
            int32_t prev_node = ITEM_2D(nexts, level - 1, node);

            if (prev_node == -1) {
                ITEM_2D(nexts, level, node) = -1;
                continue;
            }

            ITEM_2D(nexts, level, node) = ITEM_2D(nexts, level - 1, prev_node);
            ITEM_2D(costs, level, node) = ITEM_2D(costs, level - 1, node) + ITEM_2D(costs, level - 1, prev_node);
        }
    }
}


int64_t eval_path(int32_t node_a, int32_t node_b) {
    if (dsu_root(node_a) != dsu_root(node_b)) {
        return -1;
    }

    int64_t cost = 0;

    if (depths[node_a] < depths[node_b]) {
        int32_t tmp = node_a;
        node_a = node_b;
        node_b = tmp;
    }

    if (depths[node_a] != depths[node_b]) {
        const int32_t delta = depths[node_a] - depths[node_b];

        for (int32_t level = 0; level < LOG_NODES_CNT; ++level) {
            if ((delta >> level) & 1) {
                cost += ITEM_2D(costs, level, node_a);
                node_a = ITEM_2D(nexts, level, node_a);
            }
        }
    }

    if (node_a == node_b) {
        return cost;
    }

    for (int32_t level = LOG_NODES_CNT - 1; level >= 0; --level) {
        int32_t next_level_a = ITEM_2D(nexts, level, node_a);
        int32_t next_level_b = ITEM_2D(nexts, level, node_b);

        if (
            next_level_a == next_level_b ||
            next_level_a == -1 ||
            next_level_b == -1
        ) {
            continue;
        }

        cost += ITEM_2D(costs, level, node_a) + ITEM_2D(costs, level, node_b);
        node_a = next_level_a;
        node_b = next_level_b;
    }

    return cost + ITEM_2D(costs, 0, node_a) + ITEM_2D(costs, 0, node_b);
}
#pragma endregion


#pragma region Main
void solve() {
    nodes_cnt = read_int32();
    ops_cnt = read_int32();

    dsu_init();

    depths = malloc(sizeof(int32_t) * nodes_cnt);
    costs = NEW_2D(int64_t);
    nexts = NEW_2D(int32_t);
    neighbours = malloc(sizeof(struct vector) * nodes_cnt);

    for (int32_t node = 0; node < nodes_cnt; ++node) {
        depths[node] = 0;
        neighbours[node] = VECTOR_NEW(struct neighbour, 4);

        for (int32_t level = 0; level < LOG_NODES_CNT; ++level) {
            ITEM_2D(nexts, level, node) = -1;
            ITEM_2D(costs, level, node) = 0;
        }
    }

    int64_t ans = 0;

    for (int32_t iter = 0; iter < ops_cnt; ++iter) {
        int32_t op = read_int32();

        int32_t i = read_int32();
        int32_t j = read_int32();
        i = (i + ans) % nodes_cnt;
        j = (j + ans) % nodes_cnt;

        switch (op) {
        case 1: {
            int64_t cost = read_int64();
            add_edge(i, j, cost);
           
        } break;

        case 2: {
            ans = eval_path(i, j);
            printf("%lld\n", ans);
            // Should always be non-negative this way
            ans = (ans + nodes_cnt) % nodes_cnt;
        } break;
        }
    }

    // dsu_free();
}
#pragma endregion
