# Technical Report on AI-Assisted Customization for User Onboarding

## Introduction

This report details a Proof of Concept (PoC) developed using Streamlit and OpenAI's NLP technologies to automate and personalize the user onboarding process. By customizing email templates based on a user's website design and writing style, the PoC aims to boost user engagement and conversion rates. The report delves into the technical architecture, AI techniques, challenges, performance metrics, and outlines a roadmap for full-scale integration.

## Proof of Concept (PoC)

The PoC is live at [https://template-wizard.bysonduong.com/](https://template-wizard.bysonduong.com/)

(It's in the early stage, very buggy, please try multiple times with multiple inputs if the app fails)

### Architecture Overview

The PoC has been built using Streamlit for the front-end, allowing users to input the required data seamlessly. OpenAI's models are utilized for understanding design concepts, textual analysis and generation, focusing on capturing the user's writing style.

### Technology Stack

- Streamlit for frontend.
- Python's Beautiful Soup for web scraping.
- OpenAI's gpt-4 for analyzing web content and element to capture user's website design.
- OpenAI's gpt-4 for writing style analysis and text generation.

## Technical Report

### OpenAI's GPT-4 Application

OpenAI's GPT-4 is used both for extracting design elements from HTML and CSS and for capturing and applying the user's writing style to the email templates. Given its ability to understand and analyze text, GPT-4 has proven useful in distilling essential design attributes and mimicking writing styles effectively.

#### Web Design Extraction
The model reads through the HTML and CSS code of the specified web pages to identify crucial design elements like primary and secondary fonts, background colors, and more. This approach still need to improve as sometimes it fails to extract the desired information.

#### Vision-Based Alternative Approach

An alternative to the text-based parsing of HTML and CSS for design element extraction is to employ a vision-based strategy. In this approach, screenshots of key areas of the website, such as headers, body, and CTAs (Call To Action), can be captured. Subsequently, image segmentation techniques can be employed to isolate these key elements.

**Image Capture and Segmentation:**

Web pages would be rendered and screenshots captured programmatically. These images would then undergo segmentation using algorithms like U-Net, Mask R-CNN to isolate elements of interest.

**Color Extraction:**

Once the key elements are segmented, their dominant colors can be extracted from the segmented regions (a simple approach would be getting the main color). This way, primary, and secondary colors can be identified directly from the visual content, providing a more straightforward approach to color scheme extraction.

**Benefits and Challenges:**

1. **Benefits**: This approach would likely be more robust against the intricacies of modern web designs that employ complex JavaScript and dynamic content loading.
  
2. **Challenges**: It could be computationally more intensive than text-based analysis, potentially affecting the speed of the onboarding process. This approach would require data manual labeling to train new model, the current text-based approach use a already-trained model from 3rd to analyze the input, so it would take more time to prepare dataset for this vision-based approach.

By combining or choosing between the NLP-based and vision-based approaches, the system can be optimized for both performance and accuracy, adapting to a wider range of websites and design complexities.

This vision-based methodology offers a promising alternative that could be considered for integration in subsequent versions of the project, or a fallback approach if the text-based fails.

#### Writing Style Analysis
GPT-4 analyzes the textual content from the user-specified pages to understand the unique writing style. This style is then replicated in the generated email templates.

### Challenges

1. **Web Scraping**: Due to the dynamic nature of some websites, web scraping posed a considerable challenge, can be improved using 3rd party scraping services or we could allow js rendering when scraping.
2. **NLP Limitations**: GPT-4 sometimes faced difficulty in processing overly long or complex code. To address this, non-essential CSS properties were eliminated, longer text would be split to fit within GPT-4's limitations.

## Performance Metrics

There are no performance metrics in place as of now other than manually checking the result. We can create a list of webpage to check for the Color and Font Accuracy Rates, then do the evaluation against it. This can provide a more granular level of accuracy metrics for the design element extraction component. (Open for suggestion)

All in all, the ultimate goal would be reducing the time users spend for the onboarding process and improving conversion rate. Below are various approaches to assess the system’s efficacy:

### User Modification Rate

As initially suggested, one of the most direct metrics is the rate at which users modify the generated email templates. A lower rate of modification could indicate higher satisfaction and system accuracy.

### Time Spent on Onboarding

Measuring the amount of time users spend during the onboarding process can also be a key indicator. A reduced time would likely indicate a more seamless and satisfying user experience.

### User Surveys

Post-onboarding surveys asking for direct feedback can provide valuable insights into how well the design elements and writing style matched user expectations. Survey results can be quantitatively analyzed for a more data-driven understanding of system performance.

### A/B Testing

Implementing A/B tests where one group of users experiences the traditional onboarding process while another goes through the AI-assisted process can provide comparative metrics like conversion rates, user satisfaction, and retention.

### User Churn Rate

Observing the number of users who drop off during or immediately after the onboarding process can indicate whether the system adds or detracts from the overall user experience.

## Implementation Plan: System Integration and Resource Allocation

This multi-faceted plan considers the depth of AI integration, team coordination, scalability, testing methodologies, and a framework for continuous improvement.

### Phase 1: Data Preparation and Preliminary Testing (3-4 Weeks)

1. **Objective**: Prepare evaluation datasets and fine-tune the model based on the extent of AI integration desired.
2. **Resources Needed**: 
    - Product Team: Consultation
3. **Tasks**: 
    - Consult with stakeholders to determine the level of AI features desired.
    - Collect and prepare data for performance evaluation.
    - Define and communicate key performance metrics across teams.
    - Implementation to reach the desired performance.

### Phase 2: Internal Deployment and Multi-Team Coordination (2-3 Weeks)

1. **Objective**: Align with FE and BE teams for smooth integration and validation.
2. **Resources Needed**: 
    - FE Team: Consultation
    - BE Team: Consultation
3. **Tasks**: 
    - Deploy the AI system in a test environment.
    - Work with the FE team to create user-friendly interfaces.
    - Consult the BE team for scalability and optimization advice.

### Phase 3: Approval and Rollout (4-5 Weeks)

1. **Objective**: Obtain necessary approvals and roll out to a targeted user base.
2. **Tasks**: 
    - Prepare and present a rollout proposal for stakeholder approval.
    - Upon approval, work with FE and BE teams for final system integration.
    - Implement for a subset of users and monitor performance metrics.

### Continuous Improvement and Pipelines (Ongoing)

1. **Objective**: Establish pipelines for ongoing enhancements and monitoring.
2. **Resources Needed**: 
    - Part-time basis for maintenance
3. **Tasks**: 
    - Implement continuous integration and continuous deployment (CI/CD) pipelines.
    - Regularly review performance metrics and make data-driven improvements.
    - Align with Product, FE, and BE teams for phased feature releases.

### Additional Considerations

- **FE Team**: Significant FE effort will be required to create an intuitive user interface for the new AI features.

- **BE Team**: Consultation on scalability and performance is crucial for system expansion.

- **Testing Strategies**: Depending on the Product Team's direction, various testing methods such as A/B testing could be implemented to optimize user experience and feature effectiveness.

With these considerations in mind, this plan aims to offer a comprehensive, yet flexible, roadmap for the successful implementation of the AI-assisted onboarding system.
