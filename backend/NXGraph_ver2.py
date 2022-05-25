class NXGraph(nx.DiGraph):

    """
    Graph is a structure of data-vertices and process-edges. It has its own name, info and metric_types
    that can be intensive (quality, completeness) and extensive (labour expenses)
    initial_stucture is two dataframes, containing information about vertices and edges
    every hyperedge is transformed to a new vertice in the center connected with all incoming and outcoming data
    """

    def __init__(self, **args):
        super().__init__(self, **args)
        self.insp_counter("reset")

    def insp_counter(self, action: str = "small_step") -> str:
        if action == "reset":
            self.insp_count1 = 0
            self.insp_count2 = 0
            self.insp_count_tot = []
        elif action == "small_step":
            self.insp_count2 += 1
        elif action == "big_step":
            self.insp_count1 += 1
            self.insp_count_tot.append(self.insp_count2)
            self.insp_count2 = 0
        return "{}.{}. ".format(self.insp_count1, self.insp_count2)

    def build_structure(self,
                        initial_structure,
                        inspect=False,
                        model=None) -> None:
        data_df, actions_df, other = initial_structure  # others may include branches and method selection blocks
        v_set, e_set = [], []

        # Add and check nodes
        self.insp_counter("big_step")
        for _, row in data_df.iterrows():  # verify repetitions
            if model is not None:
                if row['Код модели'] != model:
                    continue

            if "," in row['name']:
                for node_name in list(map(str.strip, str(row['name']).split(','))):
                    self.add_node(node_name, **dict(row))
                if inspect:
                    print(self.insp_counter() + "Вершины {} надо задавать отдельными строками".format(row["name"]))
            else:
                self.add_node(row['name'], **dict(row))

            if inspect:
                v_set.append(row['name'])
        if 'branchings' in other:
            for _, row in other['branchings'].iterrows():
                if model is not None:
                    if row['MAIN MODEL'] != model:
                        continue
                self.add_node(row['name'], **dict(row))
                
        # Work with method selection blocks - equivalence and data joining
        methods_eq = {}
        if 'method_selection_blocks' in other:
            methods_dicts = {}
            for _, row in other['method_selection_blocks'].iterrows():
                if model is not None:
                    if row['MAIN MODEL'] != model:
                        continue
                method_name = row['name']
                method_dict = dict(row)
                if method_name in methods_dicts:
                    methods_dicts[method_name]['код\nвыхода из блока'] = method_dict['текст выбора метода']
                else:
                    methods_dicts[method_name] = method_dict
                methods_eq[row['код\nвыхода из блока']] = method_name
            for k,v in methods_dicts.items():
                self.add_node(k, **v)
                
        if inspect:
            v_set_cnt = Counter(v_set)
            for k, v in v_set_cnt.most_common():
                if v > 1:
                    print(self.insp_counter() + "Код вершины {} повторяется {} раз".format(k, v))

        # Add and check actions
        self.insp_counter("big_step")
        for _, row in actions_df.iterrows():
            if model is not None:
                if row['MAIN MODEL'] != model:
                    continue

            ins = [] if type(row['ins']) != str else list(map(str.strip, str(row['ins']).split(',')))
            if "код выхода ветвления" in row and type(row["код выхода ветвления"]) == str:
                insn = list(map(str.strip, str(row["код выхода ветвления"]).split(',')))
                for inn in insn:
                    ins += [inn[:-2]]  # отсекаются |1 |0
            outs = [] if type(row['outs']) != str else list(map(str.strip, str(row['outs']).split(',')))
            self.add_node(row['name'], **dict(row))
            if inspect:
                e_set.append(row['name'])
                if row['name'] in v_set_cnt:
                    print(self.insp_counter() + "{} одновременно ребро и вершина".format(row['name']))
            if len(ins) > 0:
                for in_node in ins:
                    if in_node in self:
                        self.add_edge(in_node, row['name'])
                    elif in_node in methods_eq and methods_eq[in_node] in self:
                        self.add_edge(methods_eq[in_node], row['name'])
                    elif inspect:
                        print(self.insp_counter() + "Входящая вершина {} ребра {} не определена".format(in_node,
                                                                                                        row['name']))
            else:
                print(self.insp_counter() + "У ребра {} нет входящих вершин".format(row['name']))

            if len(outs) > 0:
                for out_node in outs:
                    if out_node in self:
                        self.add_edge(row['name'], out_node)
                    elif out_node in methods_eq and methods_eq[out_node] in self:
                        self.add_edge(row['name'], methods_eq[out_node])
                    elif inspect:
                        print(self.insp_counter() + "Выход {} ребра {} не определен".format(out_node, row['name']))
            else:
                print(self.insp_counter() + "У ребра {} нет выходов".format(row['name']))

        self.insp_counter("big_step")
        if inspect:
            e_set_cnt = Counter(e_set)
            for k, v in e_set_cnt.most_common():
                if v > 1:
                    print(self.insp_counter() + "Код ребра {} повторяется {} раз".format(k, v))

        if inspect:
            print('Graph has {} nodes and {} edges'.format(len(self.nodes), len(self.edges)))
            print('{} simple errors found at the graph building'.format(np.sum(self.insp_count_tot)))
            comps = list(nx.weakly_connected_components(self))
            print('Found {} connected components'.format(len(comps)))
            for i, cc in enumerate(comps):
                print('{}: len={}'.format(i + 1, len(cc)))
                print(*cc)