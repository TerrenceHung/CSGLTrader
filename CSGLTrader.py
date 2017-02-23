import pickle
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import messagebox, Tk


class TradeException(Exception):
    """
    An exception to be raised when there is an error trying to make a trade.
    """
    pass


def search_item(driver, item, own_item):
    """(WebDriver, str, bool) -> None
    Searches for the item on the csgolounge search menu. If own_item is True,
    the item will be moved to the have section of the search window.
    """
    if 'keys' in item:
        driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/input').send_keys(
            'Any Key')
    elif 'Stattrak' in item:
        # click the stattrak button and search for the item
        driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/input').send_keys(
            item.lstrip('Stattrak '))
        driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/a[2]').click()
    elif own_item and 'Knife' in item:
        driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/input').send_keys(
            'Any Knife')
    elif own_item:
        # trying to trade an item that is not a key or a knife, click on Any Offers icon
        driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/input').send_keys(
            'Any Offers')
    else:
        driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/input').send_keys(item)
    # wait for the search result to appear and click it
    # sometimes clicks the first item before the search results even appear,
    # need to wait for results to disappear first
    # waiting for the loading gif to appear doesn't work, sometimes it appears too quickly'
    # WebDriverWait(driver, 3).until(EC.presence_of_element_located(
    #     (By.ID, 'loading')))
    time.sleep(1)
    # now wait for an item to appear
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/main/section[2]/div[2]/div[2]/div[2]/img'))).click()
    if own_item:
        # click the item that was added to the trade and move it to the have section
        driver.find_element_by_xpath(
            '/html/body/main/section[1]/div[1]/div/form[2]/div/div[2]/img').click()
        driver.find_element_by_xpath(
            '/html/body/main/section[1]/div[1]/div/form[2]/div/div[1]/div[2]').click()
    # disable stattrak filter if it was clicked and clear search box
    if 'Stattrak' in item:
        driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/a[2]').click()
    driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/input').clear()


def open_new_tab(driver, webelement, main_window):
    """(WebDriver, WebElement, str) -> None
    Opens the web element in a new tab, and shifts focus to the new tab.
    """
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL)
    actions.key_down(Keys.SHIFT)
    actions.click(webelement)
    actions.key_up(Keys.CONTROL)
    actions.key_up(Keys.SHIFT)
    actions.perform()
    driver.switch_to_window(main_window)


def close_tab(driver, main_window):
    """(WebDriver, str) -> None
    Closes the current tab.
    """
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
    driver.switch_to_window(main_window)


def send_trade(driver, item_to_trade, item_to_get):
    """(WebDriver, str, str) -> bool
    Opens up a trade with a user and sends a trade with the specified items.
    """
    success = True
    try:
        # open the Steam offer menu in a new tab
        open_new_tab(driver, driver.find_element_by_link_text('Steam offer'),
                     driver.current_window_handle)
        # continue if the trade menu appears
        if 'Trade offer with' in driver.title:
            try:
                # send your item first
                # expand game selection drop down menu
                WebDriverWait(driver, 2).until(EC.presence_of_element_located(
                    (By.ID, 'appselect_activeapp'))).click()
                # click on csgo, app id 730
                driver.find_element_by_id('appselect_option_you_730_2').click()
                # expand advanced filter options
                # advanced filter button disappears really quickly after selecting game
                # just delay 1 second before checking for it
                time.sleep(1)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.ID, 'filter_tag_show'))).click()
                # click on all the show more buttons
                show_more_buttons = [option for option in driver.find_elements_by_class_name(
                    'econ_tag_filter_collapsable_tags_showlink') if option.is_displayed()]
                for next_button in show_more_buttons:
                    next_button.click()
                add_to_trade(driver, item_to_trade)
                # now get other person's item
                # go to their inventory
                driver.find_element_by_id('inventory_select_their_inventory').click()
                # same thing with the advanced filter button, delay 1 sec
                time.sleep(1)
                # expand advanced filter options
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.ID, 'filter_tag_show'))).click()
                # click on all the show more buttons
                show_more_buttons = [option for option in driver.find_elements_by_class_name(
                    'econ_tag_filter_collapsable_tags_showlink') if option.is_displayed()]
                for next_button in show_more_buttons:
                    next_button.click()
                add_to_trade(driver, item_to_get)
                # items are now in trade, click ready and send trade
                driver.find_element_by_id('you_notready').click()
                # if the user did not have the item in their inventory, the warning popup will
                # appear
                no_item_warning = [warning for warning in driver.find_elements_by_class_name(
                    'ellipsis') if warning.text == 'Warning']
                # if there is no warning, send the trade
                if not no_item_warning:
                    driver.find_element_by_id('trade_confirmbtn_text').click()
                    # wait for the trade confirmation box to appear
                    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'newmodal')))
            except:
                # if anything at all went wrong in the trade then stop the current trade
                # bad design, but whatever, it's the easiest way to do it
                success = False
        else:
            success = False
        close_tab(driver, driver.current_window_handle)
    except NoSuchElementException:
        # for some reason there might be no Steam Offer button
        success = False
    close_tab(driver, driver.current_window_handle)
    return success


def add_to_trade(driver, item):
    """(WebDriver, str) -> None
    Searches for the item in the steam trade menu and adds it to the trade.
    """
    if 'keys' not in item:
        # get the web elements for the filters that are needed
        filters = {}
        for next_filter in driver.find_elements_by_class_name('econ_tag_filter_category_label'):
            if next_filter.is_displayed():
                if next_filter.text == 'Type':
                    filters['type'] = next_filter
                elif next_filter.text == 'Category':
                    filters['category'] = next_filter
                elif next_filter.text == 'Exterior':
                    filters['exterior'] = next_filter
        # click all the check boxes for the type except container and key so cases do not show up
        # in the search results
        # get the parent tag so we the boxes can be clicked
        type_options = filters['type'].find_element_by_xpath('..')
        filter_clicked = False
        for next_option in type_options.find_elements_by_class_name('econ_tag_filter_container'):
            if ('Container' not in next_option.find_element_by_class_name(
                    'econ_tag_filter_label').text and 'Key' not in next_option
                    .find_element_by_class_name('econ_tag_filter_label').text):
                # click the box if it is not container or key
                next_option.find_element_by_xpath('./input').click()
                filter_clicked = True
        if not filter_clicked:
            raise TradeException
        # check off the exterior options
        exterior_options = filters['exterior'].find_element_by_xpath('..')
        filter_clicked = False
        # now have the field for all available exterior options, go through all the options
        # and check off the correct box
        # if looking for a vanilla knife, then check off the "Not Painted" box
        if item.find('(') == -1:
            for next_option in exterior_options.find_elements_by_class_name(
                    'econ_tag_filter_container'):
                if 'Not Painted' in next_option.find_element_by_class_name(
                        'econ_tag_filter_label').text:
                    next_option.find_element_by_xpath('./input').click()
                    filter_clicked = True
        else:
            for next_option in exterior_options.find_elements_by_class_name(
                    'econ_tag_filter_container'):
                # slicing item like that will give the item condition
                if item[item.find('(') + 1:-1] in next_option.find_element_by_class_name(
                        'econ_tag_filter_label').text:
                    next_option.find_element_by_xpath('./input').click()
                    filter_clicked = True
        if not filter_clicked:
            raise TradeException
        filter_clicked = False
        if 'Stattrak' in item:
            category_options = filters['category'].find_element_by_xpath('..')
            for next_option in category_options.find_elements_by_class_name(
                    'econ_tag_filter_container'):
                if 'StatTrak' in next_option.find_element_by_class_name(
                        'econ_tag_filter_label').text:
                    next_option.find_element_by_xpath('./input').click()
                    filter_clicked = True
            if not filter_clicked:
                raise TradeException
            # strip the Stattrak and condition from the item name, then search for it
            driver.find_element_by_id('filter_control').send_keys(
                item.lstrip('Stattrak ').split(' (')[0])
        else:
            if 'Knife' not in item:
                category_options = filters['category'].find_element_by_xpath('..')
                for next_option in category_options.find_elements_by_class_name(
                        'econ_tag_filter_container'):
                    if 'Normal' in next_option.find_element_by_class_name(
                            'econ_tag_filter_label').text:
                        next_option.find_element_by_xpath('./input').click()
                        filter_clicked = True
                if not filter_clicked:
                    raise TradeException
            # strip the condition from the item name, then search for it
            driver.find_element_by_id('filter_control').send_keys(item.split(' (')[0])

        # get the html component for the 4x4 item grid
        # check for all tags with class name "inventory_page" and only get the one that is visible
        item_grid = [grid for grid in driver.find_elements_by_class_name('inventory_page') if
                     grid.is_displayed()]
        # inside this grid, add the first item, all check boxes should have filtered out anything
        # unneeded
        item_holders = [item for item in item_grid[0].find_elements_by_class_name('itemHolder') if
                        item.is_displayed()]
        try:
            actions = ActionChains(driver)
            actions.double_click(item_holders[0].find_element_by_xpath('./div'))
            actions.perform()
        except IndexError:
            # user might have a trade active on csgl but not actually have the item in their
            # inventory
            pass
    else:
        # get element with name Type and then get the parent tag so boxes can be checked
        type_filter = [filter for filter in driver.find_elements_by_class_name(
            'econ_tag_filter_category_label') if filter.is_displayed() and filter.text == 'Type']
        type_filter = type_filter[0].find_element_by_xpath('..')
        filter_clicked = False
        for next_option in type_filter.find_elements_by_class_name('econ_tag_filter_container'):
            if 'Key' in next_option.find_element_by_class_name('econ_tag_filter_label').text:
                next_option.find_element_by_xpath('./input').click()
                filter_clicked = True
        if not filter_clicked:
            raise TradeException
        # find the number of keys to add to the trade
        num_of_keys = int(item.rstrip(' keys'))
        keys_added = 0
        while keys_added < num_of_keys:
            # find all tags with class name "itemHolder", and if it is visible then it is a key
            # that can be added to the trade
            # will hold a max of 16 keys
            # this also grabs tags with class name "itemHolder trade_slot", need to filter these out
            visible_keys = [key for key in driver.find_elements_by_class_name('itemHolder')
                            if key.is_displayed() and key.get_attribute("class") == 'itemHolder']
            # add all the keys in visible_keys
            for next_key in visible_keys:
                if keys_added == num_of_keys:
                    break
                else:
                    actions = ActionChains(driver)
                    actions.double_click(next_key.find_element_by_xpath('./div'))
                    actions.perform()
                    keys_added += 1
            # added all the visible keys, so now get a new set of visible keys
            # click on the next page button
            driver.find_element_by_id('pagebtn_next').click()
            time.sleep(1)
    driver.find_element_by_id('filter_control').clear()


if __name__ == '__main__':
    # create a root window for tkinter then hide it because it looks bad
    root = Tk()
    root.withdraw()
    # open up trade history
    try:
        with open('tradehistory', 'rb') as trades:
            trade_history = pickle.load(trades)
    except EOFError:
        # if tradehistory file is blank, then set to an empty dictionary
        trade_history = {}
    # structure of trade_history:
    # {item_to_get: {steam_id: [item_to_trade]}}

    # open up trades.txt and get the trade info
    with open('trades.txt') as user_trade:
        chromedriver_path = user_trade.readline().split('\n')[0]
        MAX_NUM_TRADES = int(user_trade.readline().split('\n')[0])
        print('Number of trades to send: ', MAX_NUM_TRADES)
        item_to_get = user_trade.readline().split('\n')[0]
        print('What you are looking for: ', item_to_get)
        item_to_trade = user_trade.readline().split('\n')[0]
        print('What you are trading away: ', item_to_trade)

    # add item_to_get to trade_history if it is not in there already
    if item_to_get not in trade_history:
        trade_history[item_to_get] = {}

    # open up steam login menu on csgolounge
    driver = webdriver.Chrome(chromedriver_path)
    driver.maximize_window()
    driver.get('http://csgolounge.com/')
    try:
        assert 'CSGO Lounge' in driver.title
    except AssertionError:
        driver.quit()
        messagebox.showerror('Error', 'Please try again')
    # click login
    driver.find_element_by_xpath('/html/body/header/div[1]/a[2]').click()
    # wait for the pop up to appear then click Steam button
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/div[4]/div/div[2]/form/div/div[6]/a'))).click()
    # only continue once the user has logged into csgolounge
    logged_in = False
    while not logged_in:
        if 'CSGO Lounge' in driver.title:
            logged_in = True
    # user is now logged into csgl, click search
    driver.find_element_by_xpath('/html/body/header/nav/a[6]/img').click()
    # add user's item to trade menu first
    search_item(driver, item_to_trade, True)
    # click all items button to reset item menu
    driver.find_element_by_xpath('/html/body/main/section[2]/div[1]/form/a[1]').click()
    time.sleep(1)
    # wait for an item to appear
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/main/section[2]/div[2]/div[2]/div[2]/img')))
    # now add the item the user is looking for
    search_item(driver, item_to_get, False)
    # search for the item
    driver.find_element_by_xpath('/html/body/main/section[1]/div[1]/a').click()
    # send the max amt of trade offers, then exit
    trades_sent = 0
    while trades_sent < MAX_NUM_TRADES:
        # get a list of all 20 trades on the screen
        potential_trades = driver.find_elements_by_class_name('tradeheader')
        main_window = driver.current_window_handle
        # now have the list of trades, need to open up each trade and then check for user ids and
        # stuff
        for next_trade in potential_trades:
            open_new_tab(driver, next_trade.find_element_by_xpath('./a[2]/span/b'), main_window)
            # get their steam id from their csgl profile link
            # sometimes selenium throws a NoSuchElementException even though their profile link is
            # there so have this loop here to get the link even if an exception is thrown
            profile_found = False
            while not profile_found:
                try:
                    # everything after the = sign in their csgl profile link is their steam id
                    steam_id = driver.find_element_by_xpath(
                        '/html/body/main/section[1]/div[1]/div[1]/div/a').get_attribute(
                            'href').split('=')[1]
                    profile_found = True
                except NoSuchElementException:
                    pass
            # check if this trade has been attempted with this person already
            # if not, then proceed with sending a trade
            if steam_id not in trade_history[item_to_get]:
                trade_history[item_to_get][steam_id] = []
                if send_trade(driver, item_to_trade, item_to_get):
                    trades_sent += 1
                trade_history[item_to_get][steam_id].append(item_to_trade)
            elif item_to_trade not in trade_history[item_to_get][steam_id]:
                if send_trade(driver, item_to_trade, item_to_get):
                    trades_sent += 1
                trade_history[item_to_get][steam_id].append(item_to_trade)
            else:
                close_tab(driver, main_window)
            if trades_sent == MAX_NUM_TRADES:
                break
        # get all the page buttons, click the next one
        pages = driver.find_element_by_class_name('simplePagerNav')
        # find the one with class "currentPage", get the number, then click the button with the
        # next number
        next_page = int(pages.find_element_by_class_name('currentPage').text) + 1
        try:
            driver.find_element_by_link_text(str(next_page)).click()
        except NoSuchElementException:
            # no more pages to go through
            trades_sent = MAX_NUM_TRADES
    # write to tradehistory file
    with open('tradehistory', 'wb') as trades:
        pickle.dump(trade_history, trades)
    driver.close()
