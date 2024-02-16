import pandas as pd
import numpy as np
import ipywidgets as widgets


class GeneratorApp(object):

    def __init__(self, data_source, export_path, display_fn):
        self.data_source = data_source
        self.export_path = export_path
        self.display_fn = display_fn

        # related to teams
        self.teams = []
        self.current_team = set()

        # Extract the data
        data = pd.read_csv(data_source)

        # bring the data to our format
        self.data = pd.DataFrame.from_dict({
           'id': data.id,
            'first_name': data.first_name,
            'last_name': data.last_name,
            'email': data.email
        })



    def show_ui(self):
    # Create checkboxes for each student
        self.checkboxes = {}
        for i, row in self.data.iterrows():
            self.checkboxes[row['id']] = widgets.Checkbox(description=f"{row['id']}: {row['first_name']} {row['last_name']}")

        # Display checkboxes in a grid layout
        checkbox_grid = widgets.GridBox(list(self.checkboxes.values()), layout=widgets.Layout(grid_template_columns="repeat(3, 300px)"))
        self.display_fn(checkbox_grid)


        # Button for validation
        self.validate_button = widgets.Button(description='Create Team')
        self.show_teams_button = widgets.Button(description='Show teams')
        self.show_current_team_button = widgets.Button(description='Show current team')
        self.export_teams_button = widgets.Button(description='Export teams')

        # [validate_button, show_current_team_button, show_teams_button, export_teams_button]
        button_row = widgets.GridBox(
            [self.validate_button, self.show_current_team_button, self.show_teams_button, self.export_teams_button], 
            layout=widgets.Layout(grid_template_columns="repeat(4, 200px)"))
        self.display_fn(button_row)

        # Function to handle checkbox changes
        def handle_checkbox_change(change):
            for id_, checkbox in self.checkboxes.items():
                if checkbox == change['owner']:
                    # get the current selected or deselected student
                    current_record = self.data.where(self.data.id == id_).dropna().iloc[0].to_dict()
                    current_id = current_record['id']
                    
                    # print(current_record)

                    if change['new']:
                        self.current_team.add(current_id)
                    
                    else:
                        self.current_team.remove(current_id)

        # Attach the same handler to all checkboxes
        for checkbox in self.checkboxes.values():
            checkbox.observe(handle_checkbox_change, names='value')

        # Function to handle button click
        def handle_create_team_button_click(team_members):
            print('the current team is: {}'.format(team_members))
            # validation phase: make sure that none of the current team members were used in other teams
            if len(team_members) == 0:
                print('Please select at least one member to create a team')
                return
            
            for member in team_members:
                for t in self.teams:
                    if t.__contains__(member):
                        print('{} is already used in the team {}'.format(member, t))
                        return
            
            # add the current team to the list of teams
            self.teams.append(team_members.copy())
            
            for key, checkbox in self.checkboxes.items():
                checkbox.value = False
            self.current_team = set()


        def handle_show_teams_button_click(b):
            print('showing all teams:')
            for t in self.teams:
                print(t)

            print('---------------------------------------------')

        def handle_export_teams_button_click(teams, enable_check_found=False):
            # validation phase:
            # make sure all teams are included
            for stdid in self.data.id:
                found = False
                for t in self.teams: 
                    if t.__contains__(stdid):
                        found = True
                        break
                if not found and enable_check_found:
                    print('student with id: {} not found'.format(stdid))
                    return
            
            print('All students are found')

            # export phase
            with open(self.export_path, 'w') as f:
                for t in self.teams:
                    team_line = str.join(',', list(t))
                    f.write(team_line)
                    f.write('\n')
                f.close()


        def hand_show_current_team_button_click(b):
            print('the current team:')
            for id in self.current_team:
                s = self.data[self.data.id == id].iloc[0].to_dict()
                print(
                    "{}: {} {}".format(id, s['first_name'], s['last_name'])
                )

            print('-------------------------------------')

        # Attach the handler to the button
        self.validate_button.on_click(lambda x: handle_create_team_button_click(self.current_team))
        self.show_teams_button.on_click(handle_show_teams_button_click)
        self.show_current_team_button.on_click(hand_show_current_team_button_click)
        self.export_teams_button.on_click(lambda x: handle_export_teams_button_click(self.teams))
