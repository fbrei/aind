import logging

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def shared_subgroup(values):
    """
    Eliminate values by using the shared subgroup strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary after appling the shared subgroup rule.
    """
    
    tmp_vals = values.copy()

    rows = 'ABCDEFGHI'
    cols = '123456789'

    # Generate all boxes and units
    boxes = cross(rows,cols)
    vertical_units = [ cross(rows,col) for col in cols ]
    horizontal_units = [ cross(row,cols) for row in rows ]
    squared_units = [ cross(row,col) for row in ['ABC', 'DEF', 'GHI'] for col in ['123','456','789'] ]
    diagonal_units = [ [row+col for row,col in zip(rows,cols)], [row+col for row,col in zip(rows,cols[::-1])] ]

    # For shared subgroups we only have to iterate of 'linear' units, we will deal with the squares later
    unit_list = vertical_units + horizontal_units + diagonal_units

    # We will iterate over every possible number
    numbers = '123456789'


    for num in numbers:
        for unit in unit_list:
            # Get all the boxes that contain the current number
            boxes = [ box for box in unit if num in tmp_vals[box] ]
            
            # Only continue if there is more than one box that could contain that number (otherwise it
            # is already assigned)
            if len(boxes) > 1:
                # Check if all possible locations are inside the same square
                for square in squared_units:
                    if all( b in square for b in boxes ):
                        # If so, discard the number from all other boxes inside that square
                        for b in square:
                            if b not in boxes:
                                logging.debug("Shared Subgroup: Removing %s from %s",num,b)
                                tmp_vals[b] = tmp_vals[b].replace(num,'')

    return tmp_vals


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    tmp_vals = values.copy()

    rows = 'ABCDEFGHI'
    cols = '123456789'

    # Generate all boxes and units
    boxes = cross(rows,cols)
    vertical_units = [ cross(rows,col) for col in cols ]
    horizontal_units = [ cross(row,cols) for row in rows ]
    squared_units = [ cross(row,col) for row in ['ABC', 'DEF', 'GHI'] for col in ['123','456','789'] ]
    diagonal_units = [ [rows[i] + cols[i] for i in range(len(rows))],
                    [rows[i] + cols[len(rows)-i-1] for i in range(len(rows))] ]

    # Put them all in a single list for easier processing
    unit_list = vertical_units + horizontal_units + squared_units + diagonal_units

    for unit in unit_list:
        # Twins are pairs of boxes that each contain the same two values
        twins = [ (box1,box2) for box1 in unit for box2 in unit if len(tmp_vals[box1]) == 2 
                        and tmp_vals[box1] == tmp_vals[box2] and box1 != box2 ]

        # We can safely discard the 'twin values' from all other boxes within this unit
        for twin in twins:
            # There are exactly two values for a twin, so this is safe:
            twin1 = tmp_vals[twin[0]][0]
            twin2 = tmp_vals[twin[0]][1]
            for box in unit:
                # Of course the naked twins have to keep their values
                if box not in twin:
                    logging.debug("Naked Twins: Removing %s and %s from %s",twin1,twin2,box)
                    tmp_vals[box] = tmp_vals[box].replace(twin1,'')
                    tmp_vals[box] = tmp_vals[box].replace(twin2,'')


    return tmp_vals
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers



def cross(A, B):
    """Calculate the cross product of two arrays.
    Args:

        A(list) - the left side of the cross product
        B(list) - the right side of the cross product
    Returns:
        A list containing all possible combinations of elements from A and B
    """
    return [ s+t for s in A for t in B ]



def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    rows = 'ABCDEFGHI'
    cols = '123456789'

    boxes = cross(rows,cols)

    values = {}
    for ii in range(len(boxes)):
        values[boxes[ii]] = grid[ii].replace('.','123456789')

    return values



def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    rows = 'ABCDEFGHI'
    cols = '123456789'

    # Generate all boxes
    boxes = cross(rows,cols)

    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return



def eliminate(values):
    """
    Eliminate all values from boxes inside a unit that are already bound to a box.
    Args:
        values(dict) - Sudoku grid as a dictionary
            Keys: The boxes, e.g., 'A1'
            Values: All possible values for a box
    Returns:
        The grid dictionary, stripped off all values that are already bound.
    """

    # Make a copy of the dictionary
    tmp_vals = values.copy()

    rows = 'ABCDEFGHI'
    cols = '123456789'

    # Generate all boxes and units
    boxes = cross(rows,cols)
    vertical_units = [ cross(rows,col) for col in cols ]
    horizontal_units = [ cross(row,cols) for row in rows ]
    squared_units = [ cross(row,col) for row in ['ABC', 'DEF', 'GHI'] for col in ['123','456','789'] ]
    diagonal_units = [ [rows[i] + cols[i] for i in range(len(rows))],
                    [rows[i] + cols[len(rows)-i-1] for i in range(len(rows))] ]

    # Put them all in a single list for easier processing
    unit_list = vertical_units + horizontal_units + squared_units + diagonal_units

    # These boxes are already assigned a single value
    solved_boxes = [ box for box in boxes if len(values[box]) == 1 ]

    # Eliminate those values from all boxes within a unit that are already taken
    for box in solved_boxes:
        for unit in unit_list:
            if box in unit:
                num = values[box]
                for b in unit:
                    if b != box:
                        logging.debug("Eliminate: Removing %s from %s",num,b)
                        assign_value(values,b,tmp_vals[b].replace(num,''))
                        tmp_vals[b] = tmp_vals[b].replace(num,'')

    # And finally return the modified version of the grid dictionary
    return tmp_vals


def only_choice(values):
    """
    Assign a value to a box if no other box within the same unit can take this value.
    Arg:
        values(dict) - Sudoku grid as a dictionary
            Keys: The boxes, e.g., 'A1'
            Values: All possible values for a box
    Returns:
        The grid dictionary after assigning all only choices
    """

    # Make a copy of the dictionary
    tmp_vals = values.copy()

    rows = 'ABCDEFGHI'
    cols = '123456789'

    # We need all units again
    vertical_units = [ cross(rows,col) for col in cols ]
    horizontal_units = [ cross(row,cols) for row in rows ]
    squared_units = [ cross(row,col) for row in ['ABC', 'DEF', 'GHI'] for col in ['123','456','789'] ]
    diagonal_units = [ [rows[i] + cols[i] for i in range(len(rows))],
                    [rows[i] + cols[len(rows)-i-1] for i in range(len(rows))] ]

    # Put them all in a single list for easier processing
    unit_list = vertical_units + horizontal_units + squared_units + diagonal_units

    for unit in unit_list:
        for box in unit:
            # Fetch the possible values for all cells within this unit except for the one we are looking at
            numstring = ''
            for b in unit:
                if b != box:
                    numstring += tmp_vals[b]

            # If there is a value that does not occur anywhere else, assigned it and return to the outer loop
            for num in values[box]:
                if num not in numstring:
                    logging.debug("Only Choice: assigning %s to %s",num,box)
                    assign_value(values,box,num)
                    tmp_vals[box] = num
                    break


    return tmp_vals



def reduce_puzzle(values):
    """
    Apply only_choice and eliminate until there is no further improvement
    Args:
        values(dict) - Sudoku grid as a dictionary
            Keys: The boxes, e.g., 'A1'
            Values: All possible values for a box
    Returns:
        The grid dictionary after no futher improvements can be made
    """

    # Make a safety copy (we do not want to change the original data)
    tmp_vals = values.copy()

    # Keeps track if progress could be made
    stuck = False

    # List of heuristics to apply
    heuristics = [ eliminate, only_choice, shared_subgroup, naked_twins ]

    while not stuck:
        # The number of choices we have before applying our rules
        options_before = sum( [ len(v) for v in tmp_vals.values() if len(v) > 1 ] )

        # This order is arbitrary
        for h in heuristics:
            tmp_vals = h(tmp_vals)
        
        # Number of choices afterwards
        options_after = sum( [ len(v) for v in tmp_vals.values() if len(v) > 1 ] )

        # Did anything change?
        stuck = options_before == options_after

    return tmp_vals


def search(values):
    """
    Applies all heuristics to a sudoku grid and uses recursion if necessary
    Args:
        values(dict) - Sudoku grid as a dictionary
            Keys: The boxes, e.g., 'A1'
            Values: All possible values for a box
    Returns:
        The solved grid, or False if no solution could be found
    """

    # Try all we can without guessing
    tmp_vals = reduce_puzzle(values)

    # If there is any field that has no possible values then this attempt is wrong
    for v in values.values():
        if len(v) == 0:
            return False

    # If all boxes contain exactly one number we can return a successful solution
    if len( [ k for k in tmp_vals.keys() if len(tmp_vals[k]) == 1 ] ) == len(tmp_vals.keys()):
        return tmp_vals

    # Now we have to branch: First, find all boxes that contain more than one possible value
    candidates = [ k for k in tmp_vals.keys() if len(tmp_vals[k]) > 1 ]

    # Then choose the box with the least amount of options
    best_box = min(candidates, key = lambda x: len(tmp_vals[x]))

    # Now try assigning these values one by one and see if this leads us to a solution (recursively)
    for num in tmp_vals[best_box]:
        tmp_vals2 = tmp_vals.copy()
        tmp_vals2[best_box] = num
        result = search(tmp_vals2)
        if result:
            return result

    # Everything has failed...
    return False



def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    return search(grid_values(grid))



if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    logging.basicConfig(level=logging.INFO)

    display(solve(diag_sudoku_grid))


    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
