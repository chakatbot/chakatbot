#!/usr/bin/env python2
# -*- coding: utf-8 -*- #

from twitterbot import TwitterBot
from weasyl import Weasyl
import urllib
import os
import ConfigParser


class ChakatBot(TwitterBot):
    def bot_init(self):
        """
        Initialize and configure the bot
        """
        # Change this to your desired config file.
        self.read_config('default.ini')
        self.w_api = Weasyl(self.config['weasyl_api'])
        self.state['queue'] = []
        self.state['processed'] = []


    def make_list(self, string):
        """
        Convert a string, containing values separated by newlines, into a list
        """
        return list(filter(None, (x.strip() for x in string.splitlines())))


    def config_map(self, section, config):
        """
        Helper function for importing multiple configuration values
        """
        options = config.options(section)
        for option in options:
            try:
                self.config[option] = config.get(section, option)
                if self.config[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                self.config[option] = None


    def read_config(self, filename):
        """
        Configure the bot using an external file
        """
        config = ConfigParser.ConfigParser()
        config.read(filename)
        self.config_map('Bot', config)
        self.config['filter_strings'] = self.make_list(self.config['filter_strings'])
        self.config['ignore_strings'] = self.make_list(self.config['ignore_strings'])
        self.config['tweet_interval'] = int(self.config['tweet_interval'])
        # TODO: Read this value and others from the config file.
        self.config['tweet_interval_range'] = None
        self.config_map('Twitter', config)
        self.config_map('Weasyl', config)


    def find_in_string(self, string, category):
        """
        Return true if one of our keywords is in the string.
        Return false if only the keywords to ignore are found.

        This is determined by counting the number of instances of
        keywords, and comparing to the number of instances of words to ignore
        (which are assumed to contain one keyword each as a substring).
        """
        filter_pings = 0
        ignore_pings = 0

        for word in self.config['filter_strings']:
            if word in string.lower():
                filter_pings += 1
                self.log('Found target word: %s in %s' % (word, category))

        for word in self.config['ignore_strings']:
            if word in string.lower():
                ignore_pings += 1
                self.log('Found word to ignore: %s in %s' % (word, category))

        result = filter_pings > 0 and filter_pings > ignore_pings

        if result:
            self.log('Submission approved')

        return result


    def add_to_queue(self, submission):
        """
        Add a submission to the queue
        """
        if 'submitid' in submission:
            if not (submission['submitid'] in self.state['processed'] and
                    submission['subtype'] == 'visual'):
                self.state['queue'].append(submission['submitid'])
                self.log('Added %d to queue' % submission['submitid'])
        else:
            self.log('No submitid to add')
        return


    def download_reporthook(self, blocks_read, block_size, total_size):
        """
        Log the status of image file download
        """
        if not blocks_read:
            self.log('Connection opened')
            return
        if total_size < 0:
            self.log('Read %d blocks' % blocks_read)
        else:
            amount_read = blocks_read * block_size
            self.log('Read %d blocks, or %d/%d' % (blocks_read, amount_read, total_size))
        return


    def filter_submissions(self, submissions):
        """
        Filter a list of submissions based on keywords
        """
        self.log('Searching submissions...')
        for i in submissions:
            if (self.find_in_string(i['title'], 'title') or
               self.find_in_string("\n".join(i['tags']), 'tags')):
                self.add_to_queue(i)
            elif 'submitid' in i:
                try:
                    submission = self.w_api.view_submission(i['submitid'])
                    if (self.find_in_string(submission['description'], 'description')):
                        self.add_to_queue(i)
                except:
                    pass

        self.state['queue'].sort()
        self.log('Queued submissions: %s' % str(self.state['queue']).strip('[]'))


    def post_tweet(self, url, title, link):
        filename, msg = urllib.urlretrieve(url, reporthook=self.download_reporthook)
        if os.path.exists(filename):
            self.log('File exists:', os.path.exists(filename))
            status = link + ' ' + title
            if len(status) > 140:
                status = status[:140]
            self.api.update_with_media(filename, status)
            self.log('Posted %s with status of %s' % (filename, status))
        else:
            self.log('File missing:', os.path.exists(filename))


    def tweet_from_queue(self):
        """
        Tweet the lowest submission id in the queue
        """
        if self.state['queue']:
            submitid = self.state['queue'][0]
            self.log('Tweeting submission %d...' % submitid)
            try:
                submission = self.w_api.view_submission(submitid)
                # if there are multiple images associated with a submission,
                # only tweet the first one
                url = submission['media']['submission'][0]['url']
                title = submission['title']
                link = submission['link']

                try:
                    self.post_tweet(url, title, link)
                except:
                    self.log('Failed to post submission %d' % submitid)
                finally:
                    urllib.urlcleanup()

            except:
                self.log('Failed to retrieve submission %d' % submitid)
            finally:
                if 'processed' in self.state:
                    self.state['processed'].append(self.state['queue'].pop(0))
                else:
                    self.state['processed'] = self.state['queue'].pop(0)
        else:
            self.log('Nothing to tweet')


    def on_scheduled_tweet(self):
        """
        Scan the most recent submissions to Weasyl for keywords.
        Add any submissions that match to the queue.
        Tweet one submission from the queue.
        """
        # get 100 most recent submissions
        self.log('Retrieving most recent submissions...')
        submissions = self.w_api.frontpage()
        self.filter_submissions(submissions)
        self.tweet_from_queue()
        if self.state['queue']:
            self.log('Queued submissions remaining: %s' % str(self.state['queue']).strip('[]'))
        if self.state['processed']:
            self.log('Processed submissions: %s' % str(self.state['processed']).strip('[]'))


    def on_mention(self, tweet, prefix):
        pass

    def on_timeline(self, tweet, prefix):
        pass

if __name__ == '__main__':
    bot = ChakatBot()
    bot.run()
