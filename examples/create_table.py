import sqlite3

conn = sqlite3.connect('scores.sqlite')

conn.execute('''CREATE TABLE scores
                     (id integer primary key, emodel text, morph_dir text, morph_filename text, scores text)''')

insert_stm = 'INSERT INTO scores (emodel, morph_dir, morph_filename) VALUES (?, ?, ?)'

conn.execute(insert_stm, ('cADpyr_L5PC', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
conn.execute(insert_stm, ('cADpyr_L5PC_legacy', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
conn.execute(insert_stm, ('cADpyr_L4PC_legacy', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
conn.execute(insert_stm, ('cADpyr_L4PC', './morph_dir', 'tkb060924b2_ch5_cc2_n_og_100x_1.asc'))
conn.execute(insert_stm, ('cADpyr_L4PC', './morph_dir', 'C310897A-P4.asc'))
conn.commit()

conn.close()
