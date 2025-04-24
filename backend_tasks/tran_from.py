def opinion_to_dict(opinion,room_id):
    return {
        'main_body_mid': opinion.main_body_mid,
        'parent_comment_id': opinion.parent_comment_id,
        'main_comment_mid': opinion.main_comment_mid,
        'nickname': opinion.nickname,
        'process_content': opinion.process_content,
        'native_content': opinion.native_content,
        'reply': opinion.reply,
        'replies_count': opinion.replies_count,
        'comment_heat': opinion.comment_heat,
        'comment_location': opinion.comment_location,
        'star_num': opinion.star_num,
        'publish_time': opinion.publish_time.isoformat(),
        'sentiment': opinion.sentiment.value if opinion.sentiment else None,
        'is_ai': opinion.is_ai,
        'is_deleted': opinion.is_deleted
    }