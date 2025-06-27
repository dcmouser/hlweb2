


# casebook lark rules
JrCbLarkRule_preliminary_matter = "preliminary_matter"
JrCbLarkRule_end_matter = "end_matter"
JrCbLarkRule_level1_entry = "level1_entry"
JrCbLarkRule_level2_entry = "level2_entry"
JrCbLarkRule_level3_entry = "level3_entry"
JrCbLarkRule_overview_level1_entry = "overview_level1_entry"
#
JrCbLarkRule_level1_entry_head = "level1_entry_head"
JrCbLarkRule_level1_entry_head_overview_ = "overview_level1_entry_head"
JrCbLarkRule_level2_entry_head = "level2_entry_head"
JrCbLarkRule_level3_entry_head = "level3_entry_head"
JrCbLarkRule_entry_header = "entry_header"

JrCbLarkRule_entry_body = "entry_body"
#

JrCbLarkRule_entry_header_overview = "overview_level1_entry_head"
JrCbLarkRule_entry_id_opt_label = "entry_id_opt_label"
JrCbLarkRule_overview_level1_id = "overview_level1_id"
JrCbLarkRule_entry_id = "entry_id"
JrCbLarkRule_overview_entry_id = "overview_entry_id"
JrCbLarkRule_entry_label = "entry_label"
JrCbLarkRule_entry_options = "entry_options"
#
JrCbLarkRule_string = "string"
JrCbLarkRule_STRING_DOUBLE_QUOTE = "STRING_DOUBLE_QUOTE"
JrCbLarkRule_STRING_SINGLE_QUOTE = "STRING_SINGLE_QUOTE"
JrCbLarkRule_UNICODE_STRING = "UNICODE_STRING"
JrCbLarkRule_STRING_TRIPLE_SINGLE_QUOTE = "STRING_TRIPLE_SINGLE_QUOTE"
#
JrCbLarkRule_BlockSeq1 = "blockseq_with_newlines"
JrCbLarkRule_BlockSeq2 = "blockseq_req_newline"
JrCbLarkRule_BlockSeq3 = "blockseq_ignore_pre_newlines"
JrCbLarkRuleList_BlockSeqs = [JrCbLarkRule_BlockSeq1, JrCbLarkRule_BlockSeq2, JrCbLarkRule_BlockSeq3]
JrCbLarkRule_brace_group = "brace_group"
#
JrCbLarkRule_Block = "block"
#
JrCbLarkRule_Block_FunctionCall = "function_call"
JrCbLarkRule_Block_Text = "text_block"
JrCbLarkRule_Block_ControlStatement = "control_statement"
JrCbLarkRule_Block_Expression = "expression"
JrCbLarkRule_Block_Newline = "newline"
#
JrCbLarkRule_if_statement = "if_statement"
JrCbLarkRule_if_consequence = "if_consequence"
JrCbLarkRule_elif_statement = "elif_statement"
JrCbLarkRule_else_statement = "else_statement"
#
JrCbLarkRule_for_statement = "for_statement"
JrCbLarkRule_for_expression_in = "for_expression_in"
#
JrCbLarkRule_argument_list = "argument_list"
JrCbLarkRule_positional_argument_list = "positional_argument_list"
JrCbLarkRule_named_argument_list = "named_argument_list"
JrCbLarkRule_positional_argument = "positional_argument"
JrCbLarkRule_named_argument = "named_argument"
#
JrCbLarkRule_Operation_Binary_add = "add"
JrCbLarkRule_Operation_Binary_sub = "sub"
JrCbLarkRule_Operation_Binary_or = "or"
JrCbLarkRule_Operation_Binary_and = "and"
JrCbLarkRule_Operation_Binary_mul = "mul"
JrCbLarkRule_Operation_Binary_div = "div"
JrCbLarkRule_Operation_Binary_lessthan = "lessthan"
JrCbLarkRule_Operation_Binary_lessthanequal = "lessthanequal"
JrCbLarkRule_Operation_Binary_greaterthan = "greaterthan"
JrCbLarkRule_Operation_Binary_greaterthanequal = "greaterthanequal"
JrCbLarkRule_Operation_Binary_equal = "equal"
JrCbLarkRule_Operation_Binary_notequal = "notequal"
JrCbLarkRule_Operation_Binary_in = "in"
JrCbLarkRule_Operation_Binary_AllList = [JrCbLarkRule_Operation_Binary_add, JrCbLarkRule_Operation_Binary_sub, JrCbLarkRule_Operation_Binary_or, JrCbLarkRule_Operation_Binary_and, JrCbLarkRule_Operation_Binary_mul, JrCbLarkRule_Operation_Binary_div, JrCbLarkRule_Operation_Binary_lessthan, JrCbLarkRule_Operation_Binary_lessthanequal, JrCbLarkRule_Operation_Binary_greaterthan, JrCbLarkRule_Operation_Binary_greaterthanequal, JrCbLarkRule_Operation_Binary_equal, JrCbLarkRule_Operation_Binary_notequal, JrCbLarkRule_Operation_Binary_in]
JrCbLarkRule_Operation_Unary_neg = "neg"
JrCbLarkRule_Operation_Unary_not = "not"
JrCbLarkRule_Operation_Unary_AllList = [JrCbLarkRule_Operation_Unary_neg, JrCbLarkRule_Operation_Unary_not]
JrCbLarkRule_Atom_number = "number"
JrCbLarkRule_Atom_boolean = "boolean"
JrCbLarkRule_Atom_string = "string"
JrCbLarkRule_Atom_identifier = "identifier"
JrCbLarkRule_Atom_null = "None"
JrCbLarkRule_Atom_AllList = [JrCbLarkRule_Atom_number, JrCbLarkRule_Atom_boolean, JrCbLarkRule_Atom_string, JrCbLarkRule_Atom_identifier, JrCbLarkRule_Atom_null]
JrCbLarkRule_Collection_list = "collection_list"
JrCbLarkRule_Collection_dict = "collection_dict"
JrCbLarkRule_Collection_AllList = [JrCbLarkRule_Collection_list, JrCbLarkRule_Collection_dict]
#
JrCbLarkRule_boolean_true = "boolean_true"
JrCbLarkRule_boolean_false = "boolean_false"

# newly added for handling ## and ### sections with generic text labels
JrCbLarkRule_nonstringtextline = "nonstringtextline"
JrCbLarkRule_entry_linelabel = "entry_linelabel"

