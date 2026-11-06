The same amount checks are copy-pasted in all three split functions in splitter.py. Move them into one helper
`check_amount(paise)` and use it everywhere; behaviour and error messages must stay exactly the same.
