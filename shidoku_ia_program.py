import itertools
#only digits allowed in Shidoku
DIGITS = (1, 2, 3, 4)

# 2 representative completed boards used in paper
TYPE1 = (
    1, 2, 3, 4,
    3, 4, 1, 2,
    2, 1, 4, 3,
    4, 3, 2, 1
)

TYPE2 = (
    1, 2, 3, 4,
    3, 4, 1, 2,
    2, 3, 4, 1,
    4, 1, 2, 3
)

# pink, orange, blue, and green cell groups used in paper
UNAVOIDABLE_SETS = (
    (0, 2, 4, 6),
    (1, 3, 5, 7),
    (8, 10, 12, 14),
    (9, 11, 13, 15)
)

# creates all 288 completed Shidoku boards
def generate_boards():
    # start with an empty 16-cell board (intially has all 0s)
    board = [0] * 16
    boards = []

    #checks whether a digit can legally be placed in a cell
    def allowed(pos, value):
        row = pos // 4
        col = pos % 4

        # if digit is already in the row, column, or 2x2 box, reject it
        for c in range(4):
            if board[row * 4 + c] == value:
                return False

        for r in range(4):
            if board[r * 4 + col] == value:
                return False

        box_row = (row // 2) * 2
        box_col = (col // 2) * 2

        for r in range(box_row, box_row + 2):
            for c in range(box_col, box_col + 2):
                if board[r * 4 + c] == value:
                    return False

        # if the digit passes all three checks:
        return True

    # fills one cell at a time - for each cell it tries 1,2,3,4
    def fill(pos):
        # when all 16 cells are filled
        if pos == 16:
            boards.append(tuple(board))
            return

        for value in DIGITS:
            if allowed(pos, value):
                board[pos] = value
                #if a value is legal
                fill(pos + 1)
                # then reset the cell
                board[pos] = 0

    fill(0)
    return boards

# N(C) function from paper - goes through all 288 completed boards and sees if each one agrees with every given clue
def number_of_solutions(clues, boards):
    count = 0

    for board in boards:
        works = True
        # for each clue:
        for pos, value in clues:
            if board[pos] != value:
                works = False
                break
        # if completed bpard matches all clues
        if works:
            count += 1

    return count

# have four unavoidable sets and choose one cell from each
def minimum_candidates(board, boards):
    unique = []

    for positions in itertools.product(*UNAVOIDABLE_SETS):
        # for each choice:
        clues = tuple((pos, board[pos]) for pos in positions)
        # keeps candidate only if N(C)=1
        if number_of_solutions(clues, boards) == 1:
            unique.append(clues)

    return unique

# starts building H4 - this function creates the 8 valid row arrangements
def row_or_column_orders():
    orders = []
    # changes order of the two bands
    for block_order in itertools.permutations((0, 1)):
        # changes order of rows in each band
        for first_pair in itertools.permutations((0, 1)):
            for second_pair in itertools.permutations((0, 1)):
                pair_orders = (first_pair, second_pair)
                order = []

                for block in block_order:
                    start = 2 * block
                    order.extend(start + x for x in pair_orders[block])

                orders.append(tuple(order))

    return sorted(set(orders))

# builds all the posititon maps and stores them 
def position_maps():
    orders = row_or_column_orders()
    maps = []

    for row_order in orders:
        for col_order in orders:
            for transpose in (False, True):
                source_positions = []

                for row in range(4):
                    for col in range(4):
                        if transpose:
                            old_row = row_order[col]
                            old_col = col_order[row]
                        else:
                            old_row = row_order[row]
                            old_col = col_order[col]

                        source_positions.append(old_row * 4 + old_col)

                maps.append(tuple(source_positions))

    return sorted(set(maps))


POSITION_MAPS = position_maps()
# digit relabelings
DIGIT_PERMUTATIONS = list(itertools.permutations(DIGITS))

# physcially rearranges the cells using one of the 128 position symmetries
def apply_position(puzzle, source_positions):
    return tuple(puzzle[source] for source in source_positions)

# performs the digit relabeling
def apply_digits(puzzle, permutation):
    result = []

    for value in puzzle:
        if value == 0:
            result.append(0)
        else:
            result.append(permutation[value - 1])

    return tuple(result)

# applies all 128 position transformations and 24 digit relabelings
def orbit(puzzle):
    results = set()

    for source_positions in POSITION_MAPS:
        moved = apply_position(puzzle, source_positions)

        for permutation in DIGIT_PERMUTATIONS:
            results.add(apply_digits(moved, permutation))

    return results

# finds total of 25,728 unique four-clue puzzles
def all_unique_four_clue_puzzles(boards):
    unique = set()

    for positions in itertools.combinations(range(16), 4):
        counts = {}

        for board in boards:
            values = tuple(board[pos] for pos in positions)
            counts[values] = counts.get(values, 0) + 1

        for values, count in counts.items():
            if count == 1:
                puzzle = [0] * 16

                for pos, value in zip(positions, values):
                    puzzle[pos] = value

                unique.add(tuple(puzzle))

    return unique

# returns completed board when there is exactly one
def unique_solution(puzzle, boards):
    clues = [(pos, value) for pos, value in enumerate(puzzle) if value != 0]
    solution = None
    count = 0

    for board in boards:
        works = True

        for pos, value in clues:
            if board[pos] != value:
                works = False
                break

        if works:
            solution = board
            count += 1

    if count == 1:
        return solution

    return None

# where we get 13 classes
def classify_puzzles(unique_puzzles, boards):
    board_set = set(boards)
    # finds every completed board equivalent to the Type 1 and Type 1 representatives
    type1_boards = orbit(TYPE1) & board_set
    type2_boards = orbit(TYPE2) & board_set

    remaining = set(unique_puzzles)
    classes = []

    while remaining:
        puzzle = min(remaining)
        puzzle_orbit = orbit(puzzle) & unique_puzzles
        solution = unique_solution(puzzle, boards)

        if solution in type1_boards:
            board_type = 1
        else:
            board_type = 2
        # uses the orbit-stabilizer theorem
        orbit_size = len(puzzle_orbit)
        stabilizer_size = 3072 // orbit_size
        representative = min(puzzle_orbit)

        classes.append(
            (board_type, orbit_size, stabilizer_size, representative)
        )

        remaining -= puzzle_orbit

    classes.sort(key=lambda item: (item[0], item[1], item[3]))

    return classes, type1_boards, type2_boards


def print_puzzle(puzzle):
    for row in range(4):
        line = []

        for col in range(4):
            value = puzzle[row * 4 + col]

            if value == 0:
                line.append(".")
            else:
                line.append(str(value))

        print(" ".join(line))


def main():
    boards = generate_boards()

    type1_unique = minimum_candidates(TYPE1, boards)
    type2_unique = minimum_candidates(TYPE2, boards)

    c1 = ((0, 1), (3, 4), (13, 3), (14, 2))
    c2 = ((0, 1), (1, 2), (10, 4), (13, 3))

    unique_puzzles = all_unique_four_clue_puzzles(boards)

    classes, type1_boards, type2_boards = classify_puzzles(
        unique_puzzles, boards
    )

    print("Completed Shidoku boards:", len(boards))
    print("Type 1 completed boards:", len(type1_boards))
    print("Type 2 completed boards:", len(type2_boards))
    print()

    print("Position symmetries H4:", len(POSITION_MAPS))
    print(
        "Full symmetries G4:",
        len(POSITION_MAPS) * len(DIGIT_PERMUTATIONS)
    )
    print()

    print("Type 1 candidates tested:", 4 ** 4)
    print("Type 1 unique four-clue puzzles:", len(type1_unique))
    print("Type 2 candidates tested:", 4 ** 4)
    print("Type 2 unique four-clue puzzles:", len(type2_unique))
    print()

    print("N(C1):", number_of_solutions(c1, boards))
    print("N(C2):", number_of_solutions(c2, boards))
    print()

    print("All unique four-clue puzzles:", len(unique_puzzles))
    print("Equivalence classes:", len(classes))
    print()

    type1_number = 0
    type2_number = 0

    for board_type, orbit_size, stabilizer_size, representative in classes:
        if board_type == 1:
            type1_number += 1
            label = "Type 1-" + chr(64 + type1_number)
        else:
            type2_number += 1
            label = "Type 2-" + str(type2_number)

        print(label)
        print("Orbit size:", orbit_size)
        print("Stabilizer size:", stabilizer_size)
        print_puzzle(representative)
        print()


if __name__ == "__main__":
    main()
