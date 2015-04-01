class HphobicityScore():
    def __init__(self, name, seq, ss2_file, hydro_polyval, param_list):
        '''
        :param name: protein's name
        :param uniprot: the entrie's uniprot code
        :param seq: protein's sequence
        :param hydro_polyval: polynom valued dictionary
        :return: a stack of WinGrade instances, and their utilities
        '''
        global HP_THRESHOLD, INC_MAX, MIN_LENGTH, PSI_HELIX, PSI_RES_NUM
        HP_THRESHOLD = param_list[0]
        INC_MAX = 8
        MIN_LENGTH = param_list[1]
        PSI_HELIX = param_list[2]
        PSI_RES_NUM = param_list[3]
        self.name = name
        self.seq = seq
        self.ss2_file = ss2_file
        self.seq_length = len(seq)
        self.psipred = self.PsiReaderHelix()
        self.polyval = hydro_polyval
        # self.topo = self.topo_greedy_chooser()
        # self.n_term_orient = self.topo[0].direction
        self.WinGrades = self.win_grade_generator(0, self.seq_length, 'both')
        # self.topo_string = self.make_topo_string()
        # print 'before sort', self.WinGrades
        # self.sorted_grade = self.sort_WinGrades()
        # print 'after sort', self.sorted_grade
        # self.minimas = self.local_minima_finder(direction='both')
        # self.fwd_minimas = self.local_minima_finder(direction='fwd')
        # self.rev_minimas = self.local_minima_finder(direction='rev')
        # self.topo = self.topo_determine_new()
        # self.topo_minimas = self.topo_determine()
        # self.sorted_grade_norm = self.sort_WinGrades_norm()
        # self.minimas_norm = self.local_minima_finder_norm()
        # self.topo = self.topo_brute()
        self.topo_best, self.topo_best_val, self.topo_sec_best, self.topo_sec_best_val = self.topo_graph
        self.best_c_term = 'out' if self.topo_best[-1].direction == 'fwd' else 'in'
        self.sec_best_c_term = 'out' if self.topo_sec_best[-1].direction == 'fwd' else 'in'

    def __str__(self):
        """
        :return: A message with all Fwd/Rev minimas, and the selected topology
        """
        return 'Selectod topology:\n' + '\n'.join([str(i) for i in self.best_topo])

    # def win_grade_generator(self, pos1, pos2, fwd_or_rev):
    #     '''
    #     :return:grades all segments of self.seq, and aggregates them as WinGrades
    #     '''
    #     from WinGrade import WinGrade
    #     PSI_HP_THRESHOLD = -8.
    #     psi = self.psipred
    #     grades = []
    #     for i in range(pos1, pos2):
    #         for inc in range(min(INC_MAX, self.seq_length - 20 - i)):
    #             is_not_helical = self.is_not_helical((i, i+20+inc), psi)
    #             fwd_temp = WinGrade(i, i+20+inc, 'fwd', self.seq[i:i+20+inc], self.polyval)
    #             rev_temp = WinGrade(i, i+20+inc, 'rev', self.seq[i:i+20+inc][::-1], self.polyval)
    #             if (fwd_or_rev == 'both' or fwd_or_rev == 'fwd') and (not is_not_helical or fwd_temp.grade < PSI_HP_THRESHOLD):
    #                 grades.append(WinGrade(i, i+20+inc, 'fwd', self.seq[i:i+20+inc], self.polyval))
    #             if (fwd_or_rev == 'both' or fwd_or_rev == 'rev') and (not is_not_helical or rev_temp.grade < PSI_HP_THRESHOLD):
    #                 grades.append(WinGrade(i, i+20+inc, 'rev', self.seq[i:i+20+inc][::-1], self.polyval))
    #     return grades

    def win_grade_generator(self, pos1, pos2, fwd_or_rev):
        '''
        :return:grades all segments of self.seq, and aggregates them as WinGrades
        '''
        from WinGrade import WinGrade
        PSI_HP_THRESHOLD = -8.
        psi = self.psipred
        grades = []
        for i in range(pos1, pos2):
            for inc in range(min(INC_MAX, self.seq_length - MIN_LENGTH - i)):
                is_not_helical = self.is_not_helical((i, i+MIN_LENGTH+inc), psi)
                fwd_temp = WinGrade(i, i+MIN_LENGTH+inc, 'fwd', self.seq[i:i+MIN_LENGTH+inc], self.polyval)
                rev_temp = WinGrade(i, i+MIN_LENGTH+inc, 'rev', self.seq[i:i+MIN_LENGTH+inc][::-1], self.polyval)
                if (fwd_or_rev == 'both' or fwd_or_rev == 'fwd') and (not is_not_helical or fwd_temp.grade < PSI_HP_THRESHOLD):
                    grades.append(WinGrade(i, i+MIN_LENGTH+inc, 'fwd', self.seq[i:i+MIN_LENGTH+inc], self.polyval))
                if (fwd_or_rev == 'both' or fwd_or_rev == 'rev') and (not is_not_helical or rev_temp.grade < PSI_HP_THRESHOLD):
                    grades.append(WinGrade(i, i+MIN_LENGTH+inc, 'rev', self.seq[i:i+MIN_LENGTH+inc][::-1], self.polyval))
        return grades    

    def print_HphobicityScore(self):
        '''
        :return:a utility funciton to print things from the class
        '''
        print 'printing ', self.name
        for i in self.WinGrades:
            i.print_WinGrade()

    def sort_WinGrades(self):
        '''
        :return:a list of the WinGrades, sorted by grade
        '''
        import operator
        dict_win_grades = {i.grade: i for i in self.WinGrades}
        sort_dict = sorted(dict_win_grades.items(), key=operator.itemgetter(0))
        return [{i[0]: i[1]} for i in sort_dict]

    def local_minima_finder(self, direction):
        """
        :direction: the direction requested to m=find minimas. rev/fwd/both
        :return:returns a list of the minimal grade non-clashing WinGrades
        """
        chosen_grades = []
        i = 0
        while len(chosen_grades) == 0:
            if self.sorted_grade[i].values()[0].direction == direction or direction == 'both':
                chosen_grades = [self.sorted_grade.pop(i).values()[0]]
            i += 1
        for grade in self.sort_WinGrades():
            if direction == 'both' or (direction == grade.values()[0].direction):
                if not grade.values()[0].set_grade_colliding(chosen_grades) \
                        and grade.values()[0].grade <= HP_THRESHOLD:
                    chosen_grades.append(grade.values()[0])
        return chosen_grades

    def sort_WinGrades_norm(self):
        import operator
        dict_win_grades = {i.grade_norm: i for i in self.WinGrades}
        sort_dict = sorted(dict_win_grades.items(), key=operator.itemgetter(0))
        return [{i[0]: i[1]} for i in sort_dict]

    def local_minima_finder_norm(self):
        chosen_grades = [self.sort_WinGrades_norm().pop(0).values()[0]]
        for grade in self.sort_WinGrades_norm():
            if not grade.values()[0].set_grade_colliding(chosen_grades):
                chosen_grades.append(grade.values()[0])
        return chosen_grades

    def plot_win_grades(self):
        import matplotlib.pyplot as plt
        import matplotlib.lines as mlines
        plt.figure()
        for win_grade in self.WinGrades:
            plt.plot((win_grade.begin, win_grade.end), (win_grade.grade, win_grade.grade),
                     'k--' if win_grade.direction == 'fwd' else 'grey')
        for minima in self.topo_best:
            plt.plot((minima.begin, minima.end), (minima.grade, minima.grade),
                     color='green' if minima.direction == 'fwd' else 'purple', lw=4)
        for minima in self.topo_sec_best:
            if minima.grade > 0: continue
            plt.plot((minima.begin, minima.end), (minima.grade, minima.grade), 'b--', lw=4)
        # for minima in self.rev_minimas:
        #     if minima.grade > 0: continue
        #     plt.plot((minima.begin, minima.end), (minima.grade, minima.grade), 'r--')
        black_line = mlines.Line2D([], [], 'k--', marker='', lw=2, label='Fwd grade')
        grey_line = mlines.Line2D([], [], color='grey', marker='', lw=2, label='Rev grade')
        blue_line = mlines.Line2D([], [], color='blue', marker='', lw=2, label='Fwd minima')
        red_line = mlines.Line2D([], [], color='red', marker='', lw=2, label='Rev minima')
        green_line = mlines.Line2D([], [], color='green', marker='', lw=2, label='Fwd topo minima')
        purple_line = mlines.Line2D([], [], color='purple', marker='', lw=2, label='Rev topo minima')
        plt.legend(handles=[black_line, grey_line, blue_line, red_line, green_line, purple_line], ncol=2)
        plt.xlabel('Sequence Position')
        plt.ylabel('Energy')
        plt.title('Win Grades Energy Plot for %s' % self.name)
        plt.show()

    def topo_determine(self):
        """
        :return:a sorted list of minimas of flipping direction which has the lowest
        global energy
        """
        fwd_sorted = sorted(self.fwd_minimas, key=lambda x: x.begin)
        rev_sorted = sorted(self.rev_minimas, key=lambda x: x.begin)
        fwd_start = []
        rev_start = []
        for i in range(max([len(fwd_sorted), len(rev_sorted)])):
            fwd_start.append(fwd_sorted[i] if i % 2 == 0 and i < len(fwd_sorted) else None)
            fwd_start.append(rev_sorted[i] if i % 2 != 0 and i < len(rev_sorted) else None)
            rev_start.append(rev_sorted[i] if i % 2 == 0 and i < len(rev_sorted) else None)
            rev_start.append(fwd_sorted[i] if i % 2 != 0 and i < len(fwd_sorted) else None)
        fwd_start = [a for a in fwd_start if a is not None]
        rev_start = [a for a in rev_start if a is not None]
        fwd_score = sum([a.grade for a in fwd_start])
        rev_score = sum([a.grade for a in rev_start])
        print fwd_start
        print rev_start
        return fwd_start if fwd_score < rev_score and len(fwd_start) >= len(rev_start)\
            else rev_start

    def topo_determine_new(self):
            """
            :return:a sorted list of minimas of flipping direction which has the lowest
            global energy
            """
            fwd_sorted = sorted(self.fwd_minimas, key=lambda x: x.begin)
            rev_sorted = sorted(self.rev_minimas, key=lambda x: x.begin)
            fwd_start = []
            rev_start = []

            # for i in range(max([len(fwd_sorted), len(rev_sorted)])):
            #     fwd_start.append(fwd_sorted[i] if i % 2 == 0 and i < len(fwd_sorted) else None)
            #     fwd_start.append(rev_sorted[i] if i % 2 != 0 and i < len(rev_sorted) else None)
            #     rev_start.append(rev_sorted[i] if i % 2 == 0 and i < len(rev_sorted) else None)
            #     rev_start.append(fwd_sorted[i] if i % 2 != 0 and i < len(fwd_sorted) else None)
            fwd_start = [a for a in fwd_start if a is not None]
            rev_start = [a for a in rev_start if a is not None]
            fwd_score = sum([a.grade for a in fwd_start])
            rev_score = sum([a.grade for a in rev_start])
            print fwd_start
            print rev_start
            return fwd_start if fwd_score < rev_score and len(fwd_start) >= len(rev_start)\
                else rev_start

    def is_not_helical(self, pos, psi):
        """
        :param pos:start and end positions of the corresponding window
        :param psi: a list of alpha-helical propensity grades for the entire sequence
        :return:True if there are more than x AAs that are less helicla than y
        """
        non_helical = 0
        for i in range(pos[0], pos[1]):
            if psi[i] <= PSI_HELIX:
                non_helical += 1
        return False if non_helical < PSI_RES_NUM else True

    def PsiReaderHelix(self):
        """
        :return:reads the sequence's psipred results. returns them as a string
        """
        import re
        ss2_file = open(self.ss2_file)
        line_re = re.compile('^\s*([0-9]*)\s*([A-Z]*)\s*([A-Z]*)\s*(0\.[0-9]*)\s*(0\.[0-9]*)\s*(0\.[0-9]*)')
        result = []
        for line in ss2_file:
            if line_re.search(line):
                result.append(float(line_re.search(line).group(5)))
        return result

    def make_topo_string(self):
        in_or_out = 'out' if self.n_term_orient == 'rev' else 'in'
        tm_count = 0
        result = 'x'
        for i in range(len(self.seq)):
            if tm_count == len(self.topo):
                result += 'I' if in_or_out == 'in' else 'O'
            elif not self.topo[tm_count].pos_in_wingrade(i) and result[-1] != 'M': # not TM, and not emmidiately after TM
                result += 'I' if in_or_out == 'in' else 'O'
            elif self.topo[tm_count].pos_in_wingrade(i) and result[-1] != 'M': # first in TM
                result += 'M'
                in_or_out = 'in' if in_or_out == 'out' else 'out'
            elif self.topo[tm_count].pos_in_wingrade(i) and result[-1] == 'M': # in TM, not first
                result += 'M'
            elif not self.topo[tm_count].pos_in_wingrade(i) and result[-1] == 'M': # not in TM, emmidiatley after TM
                tm_count += 1
                result += 'I' if in_or_out == 'in' else 'O'
        return result[1:]

    def topo_greedy(self, direction):
        """
        :param direction:the direction for hte first (N') TM
        :return: a list of WinGrades starting in the desired direction, describing the minimas
        """
        big_win_len = 40
        result = []
        fwd_or_rev = direction
        i = 0
        last_end = -1
        while i < range(len(self.seq)-20):
            temp_win = self.win_grade_generator(i, i+20, fwd_or_rev)
            if len(temp_win) == 0:
                i += 1
                continue
            if temp_win[0].grade > -4.0:
                i += 1
            else:
                if i <= 10:
                    t = 0
                elif 10 < i < last_end + 1:
                    t = last_end+1
                else:
                    t = i
                win_grade_set = self.win_grade_generator(t, t+big_win_len, fwd_or_rev)
                min_grd = win_grade_set[0]
                for grd in win_grade_set:
                    if grd.grade < min_grd.grade:
                        min_grd = grd
                result.append(min_grd)
                fwd_or_rev = 'rev' if fwd_or_rev == 'fwd' else 'fwd'
                i = win_grade_set[-1].end + 1
                last_end = win_grade_set[-1].end
            if i+big_win_len > self.seq_length:
                break
        return result

    def topo_greedy_chooser(self):
        fwd = self.topo_greedy('fwd')
        rev = self.topo_greedy('rev')
        fwd_tot = sum([i.grade for i in fwd])
        rev_tot = sum([i.grade for i in rev])
        print 'fwd', fwd_tot, len(fwd)
        print 'rev', rev_tot, len(rev)
        if len(fwd) != len(rev):
            return fwd if len(fwd) > len(rev) else rev
        else:
            return fwd if fwd_tot < rev_tot else rev

    def topo_brute(self):
        from random import shuffle
        print "in brute"
        chosen_set = []
        chosen_grade = 1000
        for i in range(1000):
            all_wins = self.WinGrades[:]
            shuffle(all_wins)
            temp_set = [all_wins.pop()]
            while len(all_wins) != 0:
                temp_win = all_wins.pop()
                if not temp_win.set_grade_colliding(temp_set): temp_set.append(temp_win)
            if sum(a.grade for a in temp_set) < chosen_grade:
                chosen_set = temp_set[:]
                chosen_grade = sum(a.grade for a in temp_set)
        print chosen_set
        print chosen_grade
        return chosen_set

    def find_graph_path(self, pred, path, source_node):
        # path = [k for k, v in dist.items() if v == last_val]  # find last win
        # find all wins in the minimal energy path from source to last win
        while path[-1].seq != source_node.seq:
            for k, v in pred.items():
                if v is None:
                    continue
                if k.seq == path[-1].seq:
                    path.append(v)
        path.pop(-1)    # get rid of source_node
        return path[::-1]   # revert the path to begin->end

    @property
    def topo_graph(self):
        """
        topology determination using graph theory. wins are nodes
        :return:list of WinGrades describing best topologies
        """
        import networkx as nx
        from WinGrade import WinGrade
        import operator
        win_list = [a for a in self.WinGrades if a.grade < HP_THRESHOLD]  # make copy of negative wingrades list
        G = nx.DiGraph()
        source_node = WinGrade(0, 0, 'fwd', '', self.polyval)   # define source win
        [G.add_edge(source_node, a, weight=a.grade) for a in win_list]  # add all win to source edges
        for win1 in win_list:   # add all win to win edges where condition applies
            for win2 in win_list:
                # condition: non-overlapping, 2 is after 1, opposite directions
                if not win1.grade_grade_colliding(win2) and win2.begin > win1.end and win1.direction != win2.direction:
                    G.add_edge(win1, win2, weight=win2.grade)
        # use bellman-ford algorithm to find minimum paths to all nodes
        pred, dist = nx.bellman_ford(G, source_node)
        min_val = min(dist.values())
        best_path_val = [k for k, v in dist.items() if v == min_val]
        best_path = self.find_graph_path(pred, best_path_val, source_node)
        for k, v in sorted(dist.items(), key=operator.itemgetter(1)):
            if k.direction != best_path[-1].direction:
                sec_best_path = [k]
                sec_best_val = v
                break
        # sec_best_path, sec_best_val = [(k, v) for k, v in sorted(dist.items(), key=operator.itemgetter(1)) if k.direction != best_path[-1].direction]
        sec_best_path = self.find_graph_path(pred, sec_best_path, source_node)
        return best_path, min_val, sec_best_path, sec_best_val