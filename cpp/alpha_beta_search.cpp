/// alpha-beta search

#include <algorithm>
#include <unordered_map>
#include <utility>
#include <vector>


// the coordinate of chess
using Coordinate = std::pair<int, int>;

// a valid operation
using Operation = std::pair<Coordinate, Coordinate>;

// all ids of chesses
using ID = int;


// score of each chess
const std::unordered_map<ID, int> SCORE_TABLE = {
	{0, 0},
	{1, 100},
	{2, 3},
	{3, 4},
	{4, 1},
	{5, 2},
	{6, 5},
	{7, 6},
	{8, 12},
	{-1, -100},
	{-2, -3},
	{-3, -3},
	{-4, -1},
	{-5, -2},
	{-6, -5},
	{-7, -6},
	{-8, -12}
};


const std::unordered_map<int, std::vector<Coordinate>> DELTA = {
	{1, {{0, 1}, {0, -1}, {1, 0}, {-1, 0}}},
	{2, {{-1, -1}, {-1, 1}, {1, 1}, {1, -1}}},
	{3, {{-2, -2}, {-2, 2}, {2, 2}, {2, -2}}},
	{6, {{1, 2}, {1, -2}, {-1, 2}, {-1, -2}, {2, 1}, {2, -1}, {-2, 1}, {-2, -1}}},
	{71, {{1, 0}, {2, 0}, {3, 0}, {4, 0}, {5, 0}, {6, 0}, {7, 0}, {8, 0}, {9, 0}}},
	{72, {{-1, 0}, {-2, 0}, {-3, 0}, {-4, 0}, {-5, 0}, {-6, 0}, {-7, 0}, {-8, 0}, {-9, 0}}},
	{73, {{0, 1}, {0, 2}, {0, 3}, {0, 4}, {0, 5}, {0, 6}, {0, 7}, {0, 8}}},
	{74, {{0, -1}, {0, -2}, {0, -3}, {0, -4}, {0, -5}, {0, -6}, {0, -7}, {0, -8}}},
};


// default Operation
const Operation OPERATION = { {-1, -1}, {-1, -1} };


// Node of the min-max searching tree
class Node {
public:
	float score;
	Operation operation;

	Node(float score, Operation operation = OPERATION) {
		this->score = score;
		this->operation = operation;
	}
};


// get an evaluate score of the board data
static float evaluate(int data[10][9], float score = 0) {
	for (int i = 0; i < 10; ++i)
		for (int j = 0; j < 9; ++j)
			score += data[i][j] < 0 ? -SCORE_TABLE.at(-data[i][j]) : SCORE_TABLE.at(data[i][j]);
	return score;
}


// get all valid coordinates on board
static std::vector<Coordinate> valid_coordinate(int data[10][9], bool reverse = false) {
	std::vector<Coordinate> valid_coordinates;
	for (int i = 0; i < 10; ++i)
		for (int j = 0; j < 9; ++j)
			if ((reverse && data[i][j] < 0) || (!reverse && data[i][j] > 0))
				valid_coordinates.push_back({ i, j });
	return valid_coordinates;
}


// change the data of board
static void process(int data[10][9], int si, int sj, int ei, int ej) {
	data[ei][ej] = data[si][sj];
	data[si][sj] = 0;
	if (data[ei][ej] == -4 && ei >= 5)
		data[ei][ej] = -5;
	else if (data[ei][ej] == 4 && ei <= 4)
		data[ei][ej] = 5;
}


static bool _find(int id) {
	for (int i : {0, 2, 4, 5, 7, 9})
		return id == i;
	return false;
}


// get all possible destination of chess
static std::vector<Coordinate> possible_destination(int data[10][9], int i, int j) {
	std::vector<Coordinate> possible_destinations;
	int id = data[i][j];
	int abs_id = std::abs(id);
	int ni, nj;

	if (abs_id == 1) {
		for (auto& delta : DELTA.at(1)) {
			ni = i + delta.first, nj = j + delta.second;
			if (((0 <= ni && ni <= 2) || (7 <= ni && ni <= 9)) && 3 <= nj && nj <= 5)
				if (id * data[ni][nj] <= 0)
					possible_destinations.push_back({ ni, nj });
		}
	}
	else if (abs_id == 2) {
		for (auto& delta : DELTA.at(2)) {
			ni = i + delta.first, nj = j + delta.second;
			if (((0 <= ni && ni <= 2) || (7 <= ni && ni <= 9)) && 3 <= nj && nj <= 5)
				if (id * data[ni][nj] <= 0)
					possible_destinations.push_back({ ni, nj });
		}
	}
	else if (abs_id == 3) {
		for (auto& delta : DELTA.at(3)) {
			ni = i + delta.first, nj = j + delta.second;
			if ((_find(ni)) && 0 <= nj && nj <= 8)
				if (id * data[ni][nj] <= 0)
					if (data[(ni + i) / 2][(nj + j) / 2] == 0)
						possible_destinations.push_back({ ni, nj });
		}
	}
	else if (abs_id == 4) {
		ni = i + (id < 0 ? 1 : -1), nj = j;
		if (id * data[ni][nj] <= 0)
			possible_destinations.push_back({ ni, nj });
	}
	else if (abs_id == 5) {
		int _delta[3][2] = { {id < 0 ? 1 : -1, 0}, { 0, 1 }, {0, -1} };
		for (auto& delta : _delta) {
			ni = i + delta[0], nj = j + delta[1];
			if (0 <= ni && ni <= 9 && 0 <= nj && nj <= 8)
				if (id * data[ni][nj] <= 0)
					possible_destinations.push_back({ ni, nj });
		}
	}
	else if (abs_id == 6) {
		for (auto& delta : DELTA.at(6)) {
			ni = i + delta.first, nj = j + delta.second;
			if (0 <= ni && ni <= 9 && 0 <= nj && nj <= 8)
				if (id * data[ni][nj] <= 0)
					if (data[(int)std::round(i + delta.first / 3.)][(int)std::round(j + delta.second / 3.)] == 0)
						possible_destinations.push_back({ ni, nj });
		}
	}
	else if (abs_id == 7) {
		for (auto& deltas : { DELTA.at(71), DELTA.at(72), DELTA.at(73), DELTA.at(74) }) {
			bool stepping_stone = false;
			for (auto& delta : deltas) {
				ni = i + delta.first, nj = j + delta.second;
				if (0 <= ni && ni <= 9 && 0 <= nj && nj <= 8) {
					if (stepping_stone) {
						int key = id * data[ni][nj];
						if (key != 0) {
							if (key < 0) {
								possible_destinations.push_back({ ni, nj });
								break;
							}
							else break;
						}
					}
					else {
						if (id * data[ni][nj] != 0) stepping_stone = true;
						else possible_destinations.push_back({ ni, nj });
					}
				}
			}
		}
	}
	else if (abs_id == 8) {
		for (auto& deltas : { DELTA.at(71), DELTA.at(72), DELTA.at(73), DELTA.at(74) }) {
			for (auto& delta : deltas) {
				ni = i + delta.first, nj = j + delta.second;
				if (0 <= ni && ni <= 9 && 0 <= nj && nj <= 8) {
					if (id * data[ni][nj] == 0)
						possible_destinations.push_back({ ni, nj });
					else if (id * data[ni][nj] < 0) {
						possible_destinations.push_back({ ni, nj });
						break;
					}
					else break;
				}
			}
		}
	}
	else throw id;

	return possible_destinations;
}


// recover the data of board after operating
static void recover(int data[10][9], int si, int sj, int ei, int ej, int sv, int ev) {
	data[si][sj] = sv;
	data[ei][ej] = ev;
}


// judge whether the operation is valid
static bool valid_operation(int data[10][9], Operation operation) {
	int si = operation.first.first, sj = operation.first.second, ei = operation.second.first, ej = operation.second.second;
	bool reverse = data[si][sj] < 0;
	int key_id = reverse ? -1 : 1;
	int sv = data[si][sj], ev = data[ei][ej];
	process(data, si, sj, ei, ej);
	std::vector<Coordinate> valid_coordinates = valid_coordinate(data, !reverse);
	std::vector<Coordinate> valid_coordinates_filtered;
	for (auto& coord : valid_coordinates)
		if (std::abs(data[coord.first][coord.second]) >= 5)
			valid_coordinates_filtered.push_back(coord);
	valid_coordinates = valid_coordinates_filtered;
	for (auto& coordinate : valid_coordinates)
		for (auto& destination : possible_destination(data, coordinate.first, coordinate.second))
			if (data[destination.first][destination.second] == key_id) {
				recover(data, si, sj, ei, ej, sv, ev);
				return false;
			}
	for (int i = 0; i < 3; ++i)
		for (int j = 3; j <= 5; ++j)
			if (data[i][j] == -1) {
				for (int ni = i + 1; ni < 10; ++ni) {
					if (data[ni][j] == 0)
						continue;
					else if (data[ni][j] == 1) {
						recover(data, si, sj, ei, ej, sv, ev);
						return false;
					}
					else break;
				}
			}
	recover(data, si, sj, ei, ej, sv, ev);
	return true;
}


// get all operations
static std::vector<Operation> get_operations(int data[10][9], bool reverse = false) {
	std::vector<Operation> valid_operations;
	Operation operation;
	for (auto& coordinate : valid_coordinate(data, reverse))
		for (auto& destination : possible_destination(data, coordinate.first, coordinate.second))
			if (valid_operation(data, operation = { coordinate, destination }))
				valid_operations.push_back(operation);

	std::sort(valid_operations.begin(), valid_operations.end(), [&data](const Operation& a, const Operation& b) {
		int a_score = SCORE_TABLE.at(abs(data[a.second.first][a.second.second]));
		int b_score = SCORE_TABLE.at(abs(data[b.second.first][b.second.second]));
		return a_score > b_score;
	});

	return valid_operations;
}


// update the data of node
static std::pair<float, float> update(Node& node, Node& child, Operation& op, float alpha, float beta, bool reverse = false) {
	float temp = node.score;
	if (!reverse)
		alpha = node.score = std::max(node.score, child.score);
	else
		beta = node.score = std::min(node.score, child.score);
	if (node.score != temp)
		node.operation = op;
	return { alpha, beta };
}


// alpha value and beta value search
static Node alpha_beta_search(int data[10][9], int depth, bool reverse = false, float alpha = -INFINITY, float beta = INFINITY) {
	if (depth == 0)
		return Node(evaluate(data));
	Node node = Node(reverse ? beta : alpha);
	for (auto& op : get_operations(data, reverse)) {
		int si = op.first.first, sj = op.first.second, ei = op.second.first, ej = op.second.second;
		int sv = data[si][sj], ev = data[ei][ej];
		process(data, si, sj, ei, ej);
		Node child = alpha_beta_search(data, depth - 1, !reverse, alpha, beta);
		std::tie(alpha, beta) = update(node, child, op, alpha, beta, reverse);
		recover(data, si, sj, ei, ej, sv, ev);
		if (alpha >= beta) break;
	}
	return node;
}


// API for Python
extern "C" _declspec(dllexport) float search(int data[10][9], int depth, int result[4], bool reverse = false) {
	Node node = alpha_beta_search(data, depth, reverse);
	result[0] = node.operation.first.first;
	result[1] = node.operation.first.second;
	result[2] = node.operation.second.first;
	result[3] = node.operation.second.second;
	return node.score;
}


// API for Python
extern "C" _declspec(dllexport) void all_operations(int data[10][9], int i, int j, int operation[18][2]) {
	for (int i = 0; i < 18; ++i)
		operation[i][0] = -1;
	int count = 0;
	for (auto& destination : possible_destination(data, i, j))
		if (valid_operation(data, { { i, j }, destination })) {
			std::tie(operation[count][0], operation[count][1]) = destination;
			++count;
		}
}