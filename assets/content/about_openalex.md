### About OpenAlex API Access

This application uses the free [OpenAlex API](https://openalex.org) to search over 250 million academic papers. No API key is required.

#### Why API Rate Limits Matter

OpenAlex uses a two-tier system to ensure fair access for all users. Here's what you need to know:

> The OpenAlex API doesn't require authentication. However, it is helpful for us to know who's behind each API call, for two reasons:
>
> 1. It allows us to get in touch with the user if something's gone wrong--for instance, their script has run amok and we've needed to start blocking or throttling their usage.
>
> 2. It lets us report back to our funders, which helps us keep the lights on.
>
> Like Crossref (whose approach we are shamelessly stealing), we separate API users into two pools, the **polite pool** and the **common pool**. The polite pool has more consistent response times. It's where you want to be.
>
> To get into the polite pool, you just have to give us an email where we can contact you. You can give us this email in one of two ways:
>
> 1. Add the `mailto=you@example.com` parameter in your API request, like this: `https://api.openalex.org/works?mailto=you@example.com`
>
> 2. Add `mailto:you@example.com` somewhere in your User-Agent request header.
>
> Source: [OpenAlex API Documentation](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication)

#### For This Application

Simply enter your email in the sidebar to access the "polite pool" with faster, more consistent response times. Your email is only sent to OpenAlex and stored in your browser session.
