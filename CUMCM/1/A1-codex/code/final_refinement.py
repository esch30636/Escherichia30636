from solver import save_run

if __name__=='__main__':
    save_run('adaptive_2.5e-05',n=800,dt=1.,budget=2.5e-5,power=2.)
    save_run('space_final_1600',n=1600,dt=1.,budget=5e-5,power=2.)
