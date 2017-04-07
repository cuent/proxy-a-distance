import numpy as np
import random


class Dataset(object):
    
    def __init__(self, d1_source, d1_target, d2_source, d2_target, vocab, batch_size=64, max_seq_len=50):
        self.vocab_map = self.build_vocab_mapping(vocab)

        self.vocab_size = len(self.vocab_map)

        self.d1_source_data = self.prepare_data(d1_source)
        self.d1_target_data = self.prepare_data(d1_target)

        self.d2_source_data = self.prepare_data(d2_source)
        self.d2_target_data = self.prepare_data(d2_target)

        self.train_indices, self.val_indices, self.test_indices = self.make_splits(len(self.d1_source_data))

        self.batch_index = 0
        self.batch_size = batch_size
        self.max_seq_len = max_seq_len


    def get_vocab_size(self):
        return self.vocab_size

    def make_splits(self, N):
        indices = np.arange(N)
        train_test_n = N / 8

        train = indices[:N - (train_test_n * 2)]
        val = indices[len(train): N - train_test_n]
        test = indices[len(train) + len(val):]

        return train, val, test


    def build_vocab_mapping(self, vocabfile):
        out = {w.split()[0].strip(): i+1 for (i, w) in enumerate(open(vocabfile))}
        out['<pad>'] = 0
        return out

        
    def prepare_data(self, corpusfile):
        dataset = []
        for l in open(corpusfile):
            dataset.append([self.vocab_map.get(w, self.vocab_map['<unk>']) for w in l.split()])
        return dataset


    def mixed_batch_iter(self, train=True):
        indices = self.train_indices if train else self.test_indices
        while self.has_next_batch(indices):
            out_batch = ([], [], [], [], [])
            for i in range(self.batch_size):
                if random.random() < 0.5:
                    x, x_l, y, y_l = self.get_example(self.d1_source_data, self.d1_target_data, i)
                    out_batch[0].append(0)
                else:
                    x, x_l, y, y_l = self.get_example(self.d2_source_data, self.d2_target_data, i)
                    out_batch[0].append(1)

                out_batch[1].append(x)
                out_batch[2].append(x_l)
                out_batch[3].append(y)
                out_batch[4].append(y_l)

            yield out_batch
            self.batch_index += self.batch_size

        self.batch_index = 0
            

    def batch_iter(self, train=True):
        indices = self.train_indices if train else self.test_indices

        while self.has_next_batch(indices):
            d1_batch = self.get_batch(indices, self.d1_source_data, self.d1_target_data)
            d2_batch = self.get_batch(indices, self.d2_source_data, self.d2_target_data)
            self.batch_index += self.batch_size

        self.batch_index = 0


    def has_next_batch(self, indices):
        return self.batch_index + self.batch_size < len(indices)


    def get_example(self, source, target, i):
        def post_pad(x, pad=0):
            new =  [pad] * self.max_seq_len
            new[:len(x)] = x
            return new[:self.max_seq_len]

        x = source[self.batch_index + i]
        x = post_pad(x)
        x_l = np.count_nonzero(x)

        y = target[self.batch_index + i]
        y = post_pad(y)
        y_l = np.count_nonzero(y)

        return x, x_l, y, y_l



    def batch_iter(self, train=True):
        indices = self.train_indices if train else self.test_indices

        while self.has_next_batch(indices):
            d1_batch = self.get_batch(indices, self.d1_source_data, self.d1_target_data)
            d2_batch = self.get_batch(indices, self.d2_source_data, self.d2_target_data)
            self.batch_index += self.batch_size

        self.batch_index = 0


    def get_batch(self, indices, source_data, target_data):
        def post_pad(x, pad=0):
            new =  [pad] * self.max_seq_len
            new[:len(x)] = x
            return new[:self.max_seq_len]

        x_batch = source_data[self.batch_index : self.batch_index + self.batch_size]
        x_batch = [post_pad(x) for x in x_batch]
        x_lens = np.count_nonzero(np.array(x_batch), axis=1).tolist()

        y_batch = target_data[self.batch_index : self.batch_index + self.batch_size]
        y_batch = [post_pad(y) for y in y_batch]
        y_lens = np.count_nonzero(np.array(y_batch), axis=1).tolist()
        
        return x_batch, x_lens, y_batch, y_lens

if __name__ == '__main__':
    pass
