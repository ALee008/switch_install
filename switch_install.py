import os
import re
import csv
import glob
import string


class Switch(object):
    """

    """
    def __init__(self, path):
        self.filepath = path
        self.root, self.dirname = os.path.split(self.filepath)
        self.and_update_tag = '.and.Update.'
        self.list_of_updates_and_patches_url = 'http://www.benoitren.be/switch-gamepatches.html'

    def get_name(self):
        """

        :return: (str) game name
        """
        name = self.dirname

        if self.and_update_tag.upper() in name.upper():
            name_index_without_update_tag = string.find(name, self.and_update_tag)
            name = name[:name_index_without_update_tag]

        return name

    game_name = property(get_name)


class Game(Switch):
    def __init__(self, path):
        super(Game, self).__init__(path)

        self.contains_update = None

        self.short_name, self.extension = self.get_short_name()

        self.update = Update(self.filepath)
        self.dlc = DLC(self.filepath)

    @staticmethod
    def filter_non_game_elements(element):
        """
        Filter elements which are not relevant. Goal is to get the game file name.
        :param element: element to check condiiton.
        :return: (boolean)
        """
        if 'update'.upper() in element.upper():
            return False
        if 'upd'.upper() in element.upper():
            return False

        return True

    def get_short_name(self):
        """
        Get technical name and extension of game.
        :return:
        """
        short_name, extension = ('', '')
        for folder, sub_folder, files in os.walk(self.filepath):
            for _file in files:
                if self.filter_non_game_elements(_file):
                    short_name, extension = os.path.splitext(_file)

        return short_name, extension[1:].upper()


class Update(Switch):

    def __init__(self, path):
        super(Update, self).__init__(path)
        self.updates_path = os.path.join(self.root, '_DLC.and.Updates')
        self.update_tag = "update"
        self.update_pattern = r"\.v(?P<version>(\d|.)+)"

    def get_updates(self):
        """
        Get available updates from root and dedicated updates and dlc subfolder.
        :return: (list) list of updates with version number for a game
        """
        updates = []
        if self.update_tag.upper() in self.dirname.upper():
            update_version = re.search(self.update_pattern, self.dirname).groupdict()['version']
            updates.append(update_version)

        game_update_folders = glob.glob(os.path.join(self.updates_path, self.game_name+'*'))
        if game_update_folders:
            for update_folder in game_update_folders:
                update_version_match = re.search(self.update_pattern, update_folder)
                # if update exists
                if update_version_match:
                    update_version = update_version_match.groupdict()['version']
                    updates.append(update_version)

        return sorted(updates)

    update_versions = property(get_updates)


class DLC(Switch):
    """

    """
    def __init__(self, path):
        super(DLC, self).__init__(path)
        self.dlc_path = os.path.join(self.root, '_DLC.and.Updates')

    def get_dlcs(self):
        """
        Get available dlcs from dedicated dls folder.
        :return:
        """
        dlc_for_game = '*' + self.game_name + '*' + 'DLC' + '*'
        dlc_folders = glob.glob(os.path.join(self.dlc_path, dlc_for_game))
        dlcs = [os.path.basename(dlc) for dlc in dlc_folders]
        return dlcs

    dlcs = property(get_dlcs)


def get_game_infos(filepath):
    """
    Gather game info for later export.
    :param filepath: (str) path where games are located.
    :return: (tuple) game infos
    """
    game = Game(filepath)

    print "Processing game %s ..." % game.game_name
    game_infos = (game.game_name, game.short_name, game.extension,
                  game.update.update_versions, game.dlc.dlcs)

    print game_infos

    return game_infos


def run_collect_game_infos(games_path):
    """
    Collect all games info in result list.
    :param games_path: (str) path where games are located.
    :return: (list) each game info as element of this list.
    """
    games_abs_path = [game for game in glob.glob(games_path+r'\*')
                      if os.path.isdir(game)
                      and not os.path.basename(game).startswith('_DLC')]

    res = []

    for game_path in games_abs_path:
        res.append(get_game_infos(game_path))

    return res


def write_to_file(outfile, result_list):
    """

    :param outfile:
    :param result_list:
    :return:
    """
    header = ['game', 'short_name', 'extension', 'updates', 'dlcs']
    with open(outfile, 'wb') as outf:
        result_writer = csv.writer(outf, delimiter=';')
        result_writer.writerow(header)
        for res in result_list:
            result_writer.writerow(res)

    return None


_path = r'\\KH-NAS\Sicherungen\Games\Switch'#r'C:\temp'
t = run_collect_game_infos(_path)
write_to_file(r'C:\temp\test.csv', t)