#     Copyright 2012, Kay Hayen, mailto:kayhayen@gmx.de
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     If you submit patches or make the software available to licensors of
#     this software in either form, you automatically them grant them a
#     license for your part of the code under "Apache License 2.0" unless you
#     choose to remove this notice.
#
#     Kay Hayen uses the right to license his code under only GPL version 3,
#     to discourage a fork of Nuitka before it is "finished". He will later
#     make a new "Nuitka" release fully under "Apache License 2.0".
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, version 3 of the License.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#     Please leave the whole of this copyright notice intact.
#
""" Assignment related nodes.

All kinds of assignment targets as well as the assignment statement and expression are
located here. These are the core of value control flow.

"""

from .NodeBases import (
    CPythonExpressionChildrenHavingBase,
    CPythonChildrenHaving,
    CPythonNodeBase
)


class CPythonAssignTargetVariable( CPythonExpressionChildrenHavingBase ):
    kind = "ASSIGN_TARGET_VARIABLE"

    named_children = ( "variable_ref", )

    def __init__( self, variable_ref, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "variable_ref" : variable_ref,
            },
            source_ref = source_ref
        )

    def getDetail( self ):
        variable_ref = self.getTargetVariableRef()
        variable = variable_ref.getVariable()

        if variable is not None:
            return "to variable %s" % variable
        else:
            return "to variable %s" % self.getTargetVariableRef()

    getTargetVariableRef = CPythonExpressionChildrenHavingBase.childGetter( "variable_ref" )


class CPythonAssignTargetAttribute( CPythonExpressionChildrenHavingBase ):
    kind = "ASSIGN_TARGET_ATTRIBUTE"

    named_children = ( "expression", )

    def __init__( self, expression, attribute_name, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "expression" : expression,
            },
            source_ref = source_ref
        )

        self.attribute_name = attribute_name

    def getDetails( self ):
        return { "attribute" : self.attribute_name }

    def getDetail( self ):
        return "to attribute %s" % self.attribute_name

    def getAttributeName( self ):
        return self.attribute_name

    getLookupSource = CPythonExpressionChildrenHavingBase.childGetter( "expression" )


class CPythonAssignTargetSubscript( CPythonExpressionChildrenHavingBase ):
    kind = "ASSIGN_TARGET_SUBSCRIPT"

    named_children = ( "expression", "subscript" )

    def __init__( self, expression, subscript, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "expression" : expression,
                "subscript"  : subscript
            },
            source_ref = source_ref
        )

    getSubscribed = CPythonExpressionChildrenHavingBase.childGetter( "expression" )
    getSubscript = CPythonExpressionChildrenHavingBase.childGetter( "subscript" )


class CPythonAssignTargetSlice( CPythonExpressionChildrenHavingBase ):
    kind = "ASSIGN_TARGET_SLICE"

    named_children = ( "expression", "lower", "upper" )

    def __init__( self, expression, lower, upper, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "expression" : expression,
                "lower"      : lower,
                "upper"      : upper
            },
            source_ref = source_ref
        )

    getLookupSource = CPythonExpressionChildrenHavingBase.childGetter( "expression" )
    getUpper = CPythonExpressionChildrenHavingBase.childGetter( "upper" )
    getLower = CPythonExpressionChildrenHavingBase.childGetter( "lower" )


class CPythonAssignTargetTuple( CPythonExpressionChildrenHavingBase ):
    kind = "ASSIGN_TARGET_TUPLE"

    named_children = ( "elements", )

    def __init__( self, elements, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "elements" : tuple( elements ),
            },
            source_ref = source_ref
        )

    getElements = CPythonExpressionChildrenHavingBase.childGetter( "elements" )


class CPythonExpressionAssignment( CPythonExpressionChildrenHavingBase ):
    kind = "EXPRESSION_ASSIGNMENT"

    named_children = ( "source", "target" )

    def __init__( self, target, source, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "source" : source,
                "target" : target
            },
            source_ref = source_ref
        )

    def getDetail( self ):
        return "%s from %s" % ( self.getTarget(), self.getSource() )

    getTarget = CPythonExpressionChildrenHavingBase.childGetter( "target" )
    getSource = CPythonExpressionChildrenHavingBase.childGetter( "source" )

    def computeNode( self ):
        # TODO: Nothing to do here? Maybe if the assignment target is unused, it could
        # replace itself with source.
        return self, None, None


class CPythonStatementAssignment( CPythonChildrenHaving, CPythonNodeBase ):
    kind = "STATEMENT_ASSIGNMENT"

    named_children = ( "source", "targets" )

    def __init__( self, targets, source, source_ref ):
        CPythonNodeBase.__init__( self, source_ref = source_ref )

        CPythonChildrenHaving.__init__(
            self,
            values = {
                "source"  : source,
                "targets" : tuple( targets )
            }
        )

    def getDetail( self ):
        targets = self.getTargets()

        targets = [ target.getDetail() for target in targets ]

        if len( targets ) == 1:
            targets = targets[0]

        return "%s from %s" % ( targets, self.getSource() )

    getTargets = CPythonChildrenHaving.childGetter( "targets" )
    getSource = CPythonChildrenHaving.childGetter( "source" )


class CPythonStatementAssignmentInplace( CPythonChildrenHaving, CPythonNodeBase ):
    kind = "STATEMENT_ASSIGNMENT_INPLACE"

    named_children = ( "target", "expression" )

    def __init__( self, target, operator, expression, source_ref ):
        CPythonNodeBase.__init__( self, source_ref = source_ref )

        CPythonChildrenHaving.__init__(
            self,
            values = {
                "expression" : expression,
                "target"     : target
            }
        )

        self.operator = operator

    def getDetail( self ):
        return "to %s" % self.getTarget()

    def getOperator( self ):
        return self.operator

    getTarget = CPythonChildrenHaving.childGetter( "target" )
    getExpression = CPythonChildrenHaving.childGetter( "expression" )