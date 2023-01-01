from config.settings import settings

logger = settings.logger


def category_processor(main_category, second_category, categories):
    default_category_ID = default_category_name = default_category_name_ar = second_category_name_ar = second_category_ID = MCategory = default_category_name_parent = None
    try:
        for value in categories:
            if value['name'] == main_category:
                default_category_name_parent = value['parentId']
                default_category_name = main_category
                default_category_name_ar = value['nameTranslated']['ar']
                default_category_ID = value['id']
                
                break
            else:
                continue
            
        if second_category:
            for item in categories:
                if item['name'] == second_category and item['parentId'] == default_category_ID:
                    second_category_name_ar = item['nameTranslated']['ar']
                    second_category_ID = item['id']
                    break
                else:
                    continue

        if default_category_name:
            logger.info(
                f"Category processed successfully | Arabic: {default_category_name} | English: {default_category_name_ar}")
        else:
            logger.warning(
                f"Category {main_category} is not on the list")
            
        if default_category_name_parent:
            for value in categories:
                if value['id'] == default_category_name_parent:
                    MCategory = value['parentId']

        main_category_id = int(MCategory)

        if second_category_ID:
            categories_ids = [main_category_id,
                              default_category_ID, second_category_ID]
            categories_json = {"id": main_category_id,
                               "enabled": True}, {"id": default_category_ID,
                                                  "enabled": True}, {"id": second_category_ID,
                                                                     "enabled": True}
        elif default_category_ID == main_category_id or not default_category_ID:
            categories_ids = [main_category_id]
            categories_json = {"id": main_category_id,
                               "enabled": True}
        else:
            categories_ids = [main_category_id, default_category_ID]
            categories_json = {"id": main_category_id,
                               "enabled": True}, {"id": default_category_ID,
                                                  "enabled": True}
        logger.info("Category filling is done")

    except Exception as e:
        logger.exception(f"Category filling error occurred: {e}")
        default_category_ID = main_category_id
        categories_ids = [main_category_id]
        categories_json = {"id": main_category_id,
                           "enabled": True}

    return default_category_name_ar, second_category_name_ar, categories_ids, main_category_id, categories_json