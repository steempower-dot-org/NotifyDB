import cPickle
import json
import zlib
import gdbm
import hashlib
import memcache
import config

class BlockStore:
   def __init__(self):
       self.id_idx_db    = gdbm.open('blockid_idx.db', 'cf')
       self.num_idx_db   = gdbm.open('blocknum_idx.db','cf')
       self.blockdata_db = gdbm.open('blockdata.db' ,  'cf')
       self.mc           = memcache.Client(config.mc_endpoint)
   def reset(self):
       """ Resets the database - clears the ondisk stores and wipes cache
       """
       self.id_idx_db.close()
       self.num_idx_db.close()
       self.blockdata_db.close()
       self.mc.flush_all()
       self.id_idx_db    = gdbm.open('blockid_idx.db', 'nf')
       self.num_idx_db   = gdbm.open('blocknum_idx.db','nf')
       self.blockdata_db = gdbm.open('blockdata.db' ,  'nf')
 

   def store_block(self,block_data,block_number,block_id):
       """ block_data is the block data to be saved (duh)
           block_number and block_id may be strings or integers but will become strings
           block_data can be either JSON or a dict

           returns the DB hash on success, or None on error
       """
       if type(block_data) is str:
          db_save_data = zlib.compress(block_data)
       elif type(block_data) is dict:
          db_save_data = zlib.compress(json.dumps(block_data))
       else:
          return None

       db_save_str = db_save_data
       db_hash     = str(hashlib.sha256(db_save_str).digest())

       # here we actually store it in the DB
       self.id_idx_db[str(block_id)     ] = db_hash
       self.num_idx_db[str(block_number)] = db_hash
       self.blockdata_db[db_hash]         = db_save_str
       
       self.blockdata_db.sync() # we can rebuild an index later, so store actual block data first
       self.num_idx_db.sync()
       self.id_idx_db.sync()

       # now update memcache
       self.mc.set_multi({'ID::%s'  % str(block_id):     db_hash,
                          'NUM::%s' % str(block_number): db_hash})
       return db_hash

   def get_block(self,block_number=None,block_id=None):
       """ Try to load the specified block from the database
           Returns the block as a dict on success, None on error
       """
       mc_retval = self.mc.get_multi(['ID::%s' % str(block_id),'NUM::%s' % str(block_number)])
       db_hash = None
       for v in mc_retval.values():
           if v != None:
              db_hash = v
              break
       if db_hash == None:
          if block_number != None:
             if self.num_idx_db.has_key(block_number):
                db_hash = self.num_idx_db[str(block_number)]
          elif block_id     != None:
             if self.id_idx_db.has_key(block_id):
                db_hash = self.id_idx_db[str(block_id)]
          else:
             return None
       if db_hash == None: return None
       block_db_str  = str(self.blockdata_db[db_hash])
       block_data    = json.loads(zlib.decompress(block_db_str))
       return block_data
   
   def close(self):
       self.id_idx_db.close()
       self.num_idx_db.close()
       self.blockdata_db.close()

if __name__=='__main__':
   raw_input('WARNING: Running tests for dbstore will wipe any existing database - if you don\'t want that, hit ctrl-c now, otherwise hit enter\n')
   store    = BlockStore()
   store.reset()

   my_block = {'my_stuff':1234}
   print 'Storing dict block 1 with ID \'mystuffblock1\': %s' % str(my_block)
   print 'Return val from store_block() is (hex encoded) %s'  % str(store.store_block(my_block,1,'mystuffblock1')).encode('hex')
   
   my_block2 = json.dumps({'my_other_stuff':4567})
   print 'Storing JSON dict block 2 with ID \'myotherstuff\': %s' % str(my_block2)
   print 'Return val from store_block() is (hex encoded) %s'      % str(store.store_block(my_block2,2,'myotherstuff')).encode('hex')

   print 'Retrieving block 1 by ID: %s'                 % str(store.get_block(block_id='mystuffblock1'))
   print 'Retrieving block 1 by number: %s'             % str(store.get_block(block_number=1))
   print 'Retrieving block 1 by both number and ID: %s' % str(store.get_block(block_id='mystuffblock1',block_number=1))

   print 'Retrieving block 2 by ID: %s'                 % str(store.get_block(block_id='myotherstuff'))
   
   print 'Resetting database and closing...'
   store.reset()
   store.close()
   
   print 'Cleaning up .db files...'
   import os
   os.unlink('blockdata.db')
   os.unlink('blockid_idx.db')
   os.unlink('blocknum_idx.db')
