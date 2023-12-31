/** @odoo-module **/

import { StreamPostCommentsReplyTwitterQuote } from './stream_post_comments_reply_quote';
import { SocialPostFormatterMixin } from '@social/js/social_post_formatter_mixin';

import { Dialog } from '@web/core/dialog/dialog';
import { patch } from '@web/core/utils/patch';
import { sprintf } from '@web/core/utils/strings';
import { useService } from '@web/core/utils/hooks';

const { Component, markup } = owl;

export class StreamPostTwitterQuote extends Component {

    setup() {
        super.setup();
        this.notification = useService('notification');
    }

    _confirmQuoteTweet(event) {
        let formData = new FormData(event.currentTarget.closest('.modal-content').querySelector('form'));

        const xhr = new window.XMLHttpRequest();
        xhr.open('POST', sprintf('social_twitter/%s/quote', this.originalPost.stream_id.raw_value));
        formData.append('csrf_token', odoo.csrf_token);
        formData.append('tweet_id', this.originalPost.twitter_tweet_id.raw_value);
        formData.append('stream_id', this.originalPost.stream_id.raw_value);
        xhr.send(formData);
        xhr.onload = () => {
            const result = JSON.parse(xhr.response);
            if (result === true) {
                this.props.refreshStats();
            } else if (result.error) {
                this.notification.add(result.error, {type: 'danger'});
            }
        };
        xhr.onerror = () => {
            this.notification.add(
                this.env._t('Error while sending the data to the server.'),
                {type: 'warning'}
            );
        };
        xhr.onloadend = () => {
            this.props.close();
        };
    }

    _formatCommentStreamPost(message) {
        return markup(this._formatPost(message));
    }

    get originalPost() {
        return this.props.originalPost;
    }

    get JSON() {
        // The @StreamPostCommentsOriginalPost template needs to have JSON in its evaluation
        // context and the @TwitterQuoteDialog template inherits from it
        return JSON;
    }
}
patch(StreamPostTwitterQuote.prototype, 'social_twitter.SocialPostFormatterMixin', SocialPostFormatterMixin);

StreamPostTwitterQuote.template = "social_twitter.TwitterQuoteDialog";
StreamPostTwitterQuote.components = { Dialog, StreamPostCommentsReplyTwitterQuote };
