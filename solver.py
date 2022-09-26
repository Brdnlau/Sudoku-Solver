def encode_variable(d, i, j):
    """This function creates the variable (the integer) representing the
    fact that digit d appears in position i, j.
    Of course, to obtain the complement variable, you can just negate
    (take the negative) of the returned integer.
    Note that it must be: 1 <= d <= 9, 0 <= i <= 8, 0 <= j <= 8."""
    assert 1 <= d <= 9
    assert 0 <= i < 9
    assert 0 <= j < 9
    # The int() below seems useless, but it is not.  If d is a numpy.uint8,
    # as an element of the board is, this int() ensures that the generated
    # literal is a normal Python integer, as the SAT solvers expect.
    return int(d * 100 + i * 10 + j)
    
def decode_variable(p):
    """Given an integer constructed as by _create_prediate above,
    returns the tuple (d, i, j), where d is the digit, and i, j are
    the cells where the digit is.  Returns None if the integer is out of
    range.
    Note that it must be: 1 <= d <= 9, 0 <= i <= 8, 0 <= j <= 8.
    If this does not hold, return None.
    Also return None if p is not in the range from 100, to 988 (the
    highest and lowest values that p can assume).
    Hint: modulo arithmetic via %, // is useful here!"""
    d = p // 100
    i = (p // 10) % 10
    j = p % 10
    if d < 1 or d > 9 or i < 0 or i > 8 or j < 0 or j > 8:
        return None
    else:   
        return (d,i,j)

def every_cell_contains_at_most_one_digit():
    """Returns a list of clauses, stating that every cell contains
    at most one digit."""
    result = []
    for i in range(9):
        for j in range(9):
            for d in range(1,10):
                for dprime in range(1,10):
                    if d != dprime:
                        result.append([-(encode_variable(d,i,j)),-(encode_variable(dprime,i,j))])
    return result

def no_identical_digits_in_same_column():
    """Returns a list of clauses, stating that if a digit appears
    in a cell, the same digit cannot appear elsewhere in the
    same row, column, or 3x3 square."""
    result = []
    for j in range(9):
        for d in range(1,10):
            for i in range(9):
                for iprime in range(9):
                    if i != iprime:
                        result.append([-(encode_variable(d,i,j)),-(encode_variable(d,iprime,j))])
    return result

def sudoku_rules():
    clauses = []
    clauses.extend(every_cell_contains_at_least_one_digit())
    clauses.extend(every_cell_contains_at_most_one_digit())
    clauses.extend(no_identical_digits_in_same_row())
    clauses.extend(no_identical_digits_in_same_column())
    clauses.extend(no_identical_digits_in_same_block())
    return clauses
    
def _board_to_SAT(self):
    """Translates the currently known state of the board into a list of SAT
    clauses.  Each clause has only one literal, and expresses the fact that a
    given digit is in a given position.  The method returns the list of clauses
    corresponding to all the initially known Sudoku digits."""
    result = []
    for i in range(9):
        for j in range(9):
            if self.board[i, j] != 0:
                result.append([encode_variable(self.board[i,j], i, j)])
    return result

SudokuViaSAT._board_to_SAT = _board_to_SAT

def _to_SAT(self):
    return list(sudoku_rules()) + list(self._board_to_SAT())

SudokuViaSAT._to_SAT = _to_SAT

def solve(self, Solver):
    """Solves the Sudoku instance using the given SAT solver
    (e.g., Glucose3, Minisat22).
    @param Solver: a solver, such as Glucose3, Minisat22.
    @returns: False, if the Sudoku problem is not solvable, and True, if it is.
        In the latter case, the solve method also completes self.board,
        using the solution of SAT to complete the board."""
    with Solver() as g:
        for c in self._to_SAT():
            g.add_clause(c)
        check_equal(g.solve(), True)
        ps = g.get_model()
        for l in ps:
            if l > 0 and decode_variable(l) is not None:
                variable = decode_variable(l)
                self.board[variable[1], variable[2]] = variable[0]

SudokuViaSAT.solve = solve

def verify_solution(Solver, sudoku_string):
    sd = SudokuViaSAT(sudoku_string)
    sd.solve(Solver)
    # Check that we leave alone the original assignment.
    for i in range(9):
        for j in range(9):
            d = int(sudoku_string[i * 9 + j])
            if d > 0:
                assert sd.board[i, j] == d
    # Check that there is a digit in every cell.
    for i in range(9):
        for j in range(9):
            assert 1 <= sd.board[i, j] <= 9
    # Check the exclusion rules of Sudoku.
    for i in range(9):
        for j in range(9):
            # No repetition in row.
            for ii in range(i + 1, 9):
                assert sd.board[i, j] != sd.board[ii, j]
            # No repetition in column.
            for jj in range(j + 1, 9):
                assert sd.board[i, j] != sd.board[i, jj]
            # No repetition in block
            ci, cj = i // 3, j // 3
            for bi in range(2):
                ii = ci * 3 + bi
                for bj in range(2):
                    jj = cj * 3 + bj
                    if i != ii or j != jj:
                        assert sd.board[i, j] != sd.board[ii, jj]
