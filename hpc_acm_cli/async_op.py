from tqdm import tqdm
import time
import platform

class AsyncOp:
    class NotReady(Exception):
        pass

    def get_result(self):
        pass

# ops is a list of AsyncOp object
def async_wait(ops, handler=None, desc=None):
    total = len(ops)
    done = [False for i in range(total)]
    done_count = 0
    prog = tqdm(total=total, desc=desc, ascii=(platform.system() == 'Windows'))
    results = [None for i in range(total)] if not handler else []
    while done_count != total:
        yielded = False
        for idx, op in enumerate(ops):
            if done[idx]:
                continue
            try:
                result = op.get_result()
            except AsyncOp.NotReady:
                pass
            else:
                yielded = True
                done[idx] = True
                done_count += 1
                if handler:
                    handler(idx, result)
                else:
                    results[idx] = result
                prog.update(1)
        if not yielded:
            time.sleep(0.1)
    prog.close()
    return results

